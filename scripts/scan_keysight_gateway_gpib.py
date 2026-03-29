"""
Scan a Keysight LAN-to-GPIB gateway for instruments on one GPIB bus.

Why this script exists
----------------------
This is a bench utility.
It is meant to answer a simple question:

Which GPIB addresses respond on this gateway?

This script does not use the reusable instrument API.
It talks to the gateway directly through PyVISA.

Safety choice
-------------
The default probe is a minimal write test, not a serial poll, not a device
clear, and not an arbitrary query command.

Why:

- on this lab setup, serial poll through the gateway broke later communication
  with the HP 4192A until the instrument was power-cycled
- a minimal write probe gives up the status byte, but it is a better tradeoff
  if it keeps the bus usable afterwards

How to use
----------
1. Run:

   python scripts/scan_keysight_gateway_gpib.py

2. Type the gateway IP address when prompted.
3. Wait for the scan to finish.
4. Read the list of responding GPIB addresses.

Optional behavior
-----------------
If you want to try `*IDN?` on devices that respond, set `TRY_SCPI_IDN = True`.

Important:
`*IDN?` is only for SCPI instruments. Older HP-IB instruments may not support it.
"""

from __future__ import annotations

import time

import pyvisa


# Leave this empty to type the IP address when the script starts.
DEFAULT_GATEWAY_IP = ""

# Most users of this gateway will scan bus 0 first.
GPIB_BUS = 0

# Typical instrument addresses live in this range.
START_ADDRESS = 1
END_ADDRESS = 30

# Timeout in milliseconds for each address check.
TIMEOUT_MS = 1000

# Probe method.
#
# "blank_write":
#     Open the address and send a single linefeed byte. On a real listener this
#     should complete. On an empty address it should fail with a no-listener /
#     timeout style error. This is the default because serial poll broke the
#     HP 4192A communication path in this setup.
#
# "serial_poll":
#     Read the status byte. This is kept only as an optional fallback for other
#     setups. It is not the default anymore.
PROBE_METHOD = "blank_write"

# Optional extra step for SCPI instruments only.
TRY_SCPI_IDN = False

# Byte sequence used by the blank-write probe.
BLANK_WRITE_BYTES = b"\n"

# After probing one address, explicitly return the instrument to a released
# local state if the VISA backend supports it.
RELEASE_TO_LOCAL_AFTER_PROBE = True

# Small pause after bus cleanup. This gives the gateway and instrument a moment
# to settle before the next access.
POST_CLEANUP_DELAY_S = 0.05

# After the entire scan, try to return the gateway GPIB controller itself to a
# neutral state. This is a bus-level cleanup, not an instrument-level command.
SEND_IFC_AFTER_SCAN = True


def ask_gateway_ip() -> str:
    """
    Return the gateway IP address.

    If DEFAULT_GATEWAY_IP is empty, ask the user to type it.
    """

    if DEFAULT_GATEWAY_IP.strip():
        return DEFAULT_GATEWAY_IP.strip()

    gateway_ip = input("Gateway IP address: ").strip()
    if not gateway_ip:
        raise RuntimeError("No gateway IP address was entered.")

    return gateway_ip


def build_resource_name(gateway_ip: str, gpib_address: int) -> str:
    return f"TCPIP0::{gateway_ip}::gpib{GPIB_BUS},{gpib_address}::INSTR"


def try_scpi_idn(inst) -> str | None:
    """
    Try a SCPI identification query.

    This is optional because many older instruments are not SCPI-based.
    """

    if not TRY_SCPI_IDN:
        return None

    try:
        return str(inst.query("*IDN?")).strip()
    except Exception:
        return None


def release_probe_session(inst) -> None:
    """
    Try to leave the probed instrument in a clean local/idle state.

    Why this exists
    ---------------
    Some instruments and LAN-to-GPIB gateways keep talking or stay busy even
    after the Python resource object is closed. The likely reason is that the
    GPIB remote-enable state was not explicitly released.

    This helper tries to send "go to local" together with REN deassertion.
    If the backend or resource does not support it, the scan still continues.
    """

    if not RELEASE_TO_LOCAL_AFTER_PROBE:
        return

    if not hasattr(inst, "control_ren"):
        return

    try:
        inst.control_ren(pyvisa.constants.RENLineOperation.deassert_gtl)
    except Exception:
        # Some VISA backends or gateway/resource combinations do not support
        # control_ren on this kind of session. In that case we fall back to a
        # normal close.
        pass


def configure_probe_session(inst) -> None:
    """
    Ask VISA to unaddress the GPIB device after I/O when possible.

    Why this exists
    ---------------
    Keysight VISA exposes a GPIB-specific attribute that controls whether a
    device is explicitly unaddressed after each transfer. The default is not
    ideal for a scan utility, because we want each probe to leave as little
    state behind on the bus as possible.
    """

    try:
        inst.set_visa_attribute(
            pyvisa.constants.ResourceAttribute.gpib_unadress_enable,
            True,
        )
    except Exception:
        pass

    try:
        inst.set_visa_attribute(
            pyvisa.constants.ResourceAttribute.send_end_enabled,
            True,
        )
    except Exception:
        pass


def probe_device(inst) -> dict[str, object]:
    """
    Probe one open VISA resource and return a small result dictionary.

    The returned keys are intentionally simple so the scan summary stays easy
    to read.
    """

    if PROBE_METHOD == "serial_poll":
        status_byte = int(inst.read_stb())
        return {
            "probe": "serial_poll",
            "status_byte": status_byte,
        }

    if PROBE_METHOD == "blank_write":
        if hasattr(inst, "write_raw"):
            inst.write_raw(BLANK_WRITE_BYTES)
        else:
            inst.write(BLANK_WRITE_BYTES.decode("ascii"))

        return {
            "probe": "blank_write",
            "status_byte": None,
        }

    raise ValueError(f"Unsupported PROBE_METHOD: {PROBE_METHOD!r}")


def cleanup_gateway_controller(resource_manager, gateway_ip: str) -> None:
    """
    Return the LAN-to-GPIB gateway controller to an idle bus state.

    Why this exists
    ---------------
    Closing individual instrument sessions may still leave the controller side
    of the gateway in a state that interferes with the next script. Sending an
    interface clear is a controller-level reset of bus handshaking, not a
    device-clear command to the instrument.
    """

    if not SEND_IFC_AFTER_SCAN:
        return

    interface_name = f"TCPIP0::{gateway_ip}::INTFC"
    interface = None

    try:
        interface = resource_manager.open_resource(interface_name)

        if hasattr(interface, "send_ifc"):
            interface.send_ifc()

        if hasattr(interface, "control_ren"):
            try:
                interface.control_ren(pyvisa.constants.RENLineOperation.deassert)
            except Exception:
                pass
    except Exception:
        pass
    finally:
        if interface is not None:
            try:
                interface.close()
            except Exception:
                pass


def scan_gateway_bus(gateway_ip: str) -> list[dict[str, object]]:
    """
    Scan one GPIB bus on the gateway.

    A successful probe is treated as "device present".
    """

    results: list[dict[str, object]] = []
    resource_manager = pyvisa.ResourceManager()

    try:
        for address in range(START_ADDRESS, END_ADDRESS + 1):
            resource_name = build_resource_name(gateway_ip, address)
            print(f"Checking address {address:02d}: {resource_name}")

            inst = None
            try:
                inst = resource_manager.open_resource(resource_name)
                inst.timeout = TIMEOUT_MS
                configure_probe_session(inst)

                probe_result = probe_device(inst)
                idn = try_scpi_idn(inst)

                print(f"  Found device. Probe: {probe_result['probe']}")
                if probe_result["status_byte"] is not None:
                    print(f"  Status byte: {probe_result['status_byte']}")
                if idn:
                    print(f"  SCPI IDN: {idn}")

                results.append(
                    {
                        "address": address,
                        "resource_name": resource_name,
                        "status_byte": probe_result["status_byte"],
                        "probe": probe_result["probe"],
                        "idn": idn,
                    }
                )
            except Exception:
                print("  No response.")
            finally:
                if inst is not None:
                    release_probe_session(inst)
                    try:
                        inst.close()
                    except Exception:
                        pass
                    if POST_CLEANUP_DELAY_S > 0:
                        time.sleep(POST_CLEANUP_DELAY_S)
    finally:
        cleanup_gateway_controller(resource_manager, gateway_ip)
        resource_manager.close()

    return results


def print_summary(results: list[dict[str, object]]) -> None:
    print()
    print("Scan summary")
    print("------------")

    if not results:
        print("No responding GPIB addresses were found.")
        return

    for result in results:
        print(f"Address {result['address']:02d}: {result['resource_name']}")
        print(f"  probe: {result['probe']}")
        if result["status_byte"] is not None:
            print(f"  status byte: {result['status_byte']}")
        if result["idn"]:
            print(f"  SCPI IDN: {result['idn']}")


def main() -> None:
    print("Keysight gateway GPIB scan")
    print("--------------------------")
    print(f"GPIB bus: {GPIB_BUS}")
    print(f"Address range: {START_ADDRESS} to {END_ADDRESS}")
    print(f"Timeout: {TIMEOUT_MS} ms")
    print(f"Probe method: {PROBE_METHOD}")
    if TRY_SCPI_IDN:
        print("SCPI IDN probe: on")
    else:
        print("SCPI IDN probe: off")
    print()

    gateway_ip = ask_gateway_ip()
    print(f"Gateway IP: {gateway_ip}")
    print()

    results = scan_gateway_bus(gateway_ip)
    print_summary(results)


if __name__ == "__main__":
    main()

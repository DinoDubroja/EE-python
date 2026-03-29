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
The default probe is a serial poll (`read_stb()`), not a device clear and not
an arbitrary query command. That makes this script safer for older instruments.

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

import pyvisa
from pyvisa.resources.gpib import GPIBCommand


# Leave this empty to type the IP address when the script starts.
DEFAULT_GATEWAY_IP = ""

# Most users of this gateway will scan bus 0 first.
GPIB_BUS = 0

# Typical instrument addresses live in this range.
START_ADDRESS = 1
END_ADDRESS = 30

# Timeout in milliseconds for each address check.
TIMEOUT_MS = 1000

# Optional extra step for SCPI instruments only.
TRY_SCPI_IDN = False

# After probing one address, explicitly return the instrument to a released
# local state if the VISA backend supports it. On older GPIB instruments and
# gateways, closing the VISA session alone is sometimes not enough.
RELEASE_TO_LOCAL_AFTER_PROBE = True

# After a serial poll, explicitly disable serial-poll mode and unaddress the
# bus. Some older instruments appear to remain in a bad communication state if
# this is not done cleanly by the backend or gateway.
SEND_SERIAL_POLL_CLEANUP = True

# Small pause after bus cleanup. This gives the gateway and instrument a moment
# to settle before the next access.
POST_CLEANUP_DELAY_S = 0.05


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


def build_interface_resource_name(gateway_ip: str) -> str:
    return f"TCPIP0::{gateway_ip}::gpib{GPIB_BUS}::INTFC"


def cleanup_after_serial_poll(interface_resource) -> None:
    """
    Explicitly unwind serial-poll bus state.

    Why this exists
    ---------------
    The HP 4192A appears to be sensitive to the serial-poll path used during a
    GPIB scan. Even when the VISA session is closed, the instrument can stay in
    a broken communication state until it is power-cycled.

    This helper sends the low-level GPIB commands that should end a serial poll
    and leave the bus unaddressed:

    - SPD: serial poll disable
    - UNT: untalk
    - UNL: unlisten
    """

    if not SEND_SERIAL_POLL_CLEANUP:
        return

    if interface_resource is None or not hasattr(interface_resource, "send_command"):
        return

    try:
        interface_resource.send_command(
            GPIBCommand.serial_poll_disable
            + GPIBCommand.untalk
            + GPIBCommand.unlisten
        )
    except Exception:
        pass


def scan_gateway_bus(gateway_ip: str) -> list[dict[str, object]]:
    """
    Scan one GPIB bus on the gateway.

    A responding status byte is treated as "device present".
    """

    results: list[dict[str, object]] = []
    resource_manager = pyvisa.ResourceManager()
    interface_resource = None

    try:
        try:
            interface_resource = resource_manager.open_resource(
                build_interface_resource_name(gateway_ip)
            )
        except Exception:
            interface_resource = None

        for address in range(START_ADDRESS, END_ADDRESS + 1):
            resource_name = build_resource_name(gateway_ip, address)
            print(f"Checking address {address:02d}: {resource_name}")

            inst = None
            try:
                inst = resource_manager.open_resource(resource_name)
                inst.timeout = TIMEOUT_MS

                status_byte = int(inst.read_stb())
                idn = try_scpi_idn(inst)

                print(f"  Found device. Status byte: {status_byte}")
                if idn:
                    print(f"  SCPI IDN: {idn}")

                results.append(
                    {
                        "address": address,
                        "resource_name": resource_name,
                        "status_byte": status_byte,
                        "idn": idn,
                    }
                )
            except Exception:
                print("  No response.")
            finally:
                if inst is not None:
                    cleanup_after_serial_poll(interface_resource)
                    release_probe_session(inst)
                    try:
                        inst.close()
                    except Exception:
                        pass
                    if POST_CLEANUP_DELAY_S > 0:
                        import time

                        time.sleep(POST_CLEANUP_DELAY_S)
    finally:
        if interface_resource is not None:
            try:
                cleanup_after_serial_poll(interface_resource)
            except Exception:
                pass
            try:
                interface_resource.close()
            except Exception:
                pass
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
        print(f"  status byte: {result['status_byte']}")
        if result["idn"]:
            print(f"  SCPI IDN: {result['idn']}")


def main() -> None:
    print("Keysight gateway GPIB scan")
    print("--------------------------")
    print(f"GPIB bus: {GPIB_BUS}")
    print(f"Address range: {START_ADDRESS} to {END_ADDRESS}")
    print(f"Timeout: {TIMEOUT_MS} ms")
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

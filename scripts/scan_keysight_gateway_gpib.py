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


def scan_gateway_bus(gateway_ip: str) -> list[dict[str, object]]:
    """
    Scan one GPIB bus on the gateway.

    A responding status byte is treated as "device present".
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
                    try:
                        inst.close()
                    except Exception:
                        pass
    finally:
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

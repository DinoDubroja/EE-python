"""
Read one HP 4192A measurement through the high-level API.

Purpose
-------
Use this script when you want the simplest possible real-hardware check of the
`measure()` function.

By default, the script does not change the instrument setup. It simply reads
whatever the instrument is currently configured to show on DISPLAY A and
DISPLAY B.

Optional behavior
-----------------
If you want the script to first force a known display pair, set
`SET_KNOWN_DISPLAY = True` below.

How to use
----------
1. Edit `RESOURCE`.
2. If you want, change `SET_KNOWN_DISPLAY`.
3. Run:

   python examples/hp_4192a/read_measurement.py
"""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "source"
sys.path.insert(0, str(SOURCE_DIR))

from instruments import HP4192A  # noqa: E402


RESOURCE = "TCPIP0::192.168.1.244::gpib0,5::INSTR"
TIMEOUT_MS = 5000

# Leave this False if you want to measure the instrument exactly as it is
# already configured on the bench.
SET_KNOWN_DISPLAY = False

# These settings are only used when SET_KNOWN_DISPLAY is True.
KNOWN_DISPLAY_A = "impedance"
KNOWN_DISPLAY_B = "phase_deg"


def main() -> None:
    print("HP 4192A read_measurement example")
    print("---------------------------------")
    print(f"Resource: {RESOURCE}")

    meter = HP4192A.open(RESOURCE, timeout_ms=TIMEOUT_MS)

    try:
        if SET_KNOWN_DISPLAY:
            print()
            print("Setting a known display pair before measure()...")
            meter.configure(
                display_a=KNOWN_DISPLAY_A,
                display_b=KNOWN_DISPLAY_B,
            )

        print()
        print("Calling measure()...")
        reading = meter.measure()

        print()
        print(reading.to_text())

        print()
        print("Access individual values in Python like this:")
        print(f"  reading.display_a.label = {reading.display_a.label!r}")
        print(f"  reading.display_a.value = {reading.display_a.value!r}")
        print(f"  reading.display_b.label = {reading.display_b.label!r}")
        print(f"  reading.display_b.value = {reading.display_b.value!r}")
        print(f"  reading.display_c.unit_code = {reading.display_c.unit_code!r}")
        print(f"  reading.display_c.raw_value = {reading.display_c.raw_value!r}")
    finally:
        meter.close()
        print()
        print("Connection closed.")


if __name__ == "__main__":
    main()

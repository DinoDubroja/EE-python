"""
Simple real-hardware check for the HP 4192A frequency API.

What this script does
---------------------
1. Opens the HP 4192A
2. Calls ping() and prints the current state report
3. Sets a new spot frequency with configure(frequency_hz=...)
4. Calls ping() again so you can see the updated frequency
5. Closes the connection

Why this exists
---------------
This script is meant for bench use.
It is intentionally simple and does not use command-line arguments.
Edit the values below, run the script, and watch the instrument.

How to use
----------
1. Edit RESOURCE if needed.
2. Edit TARGET_FREQUENCY_HZ to the frequency you want to send.
3. Run:

   python examples/hp_4192a/check_frequency.py

4. Watch the front panel and compare it with the printed ping() output.
"""

from __future__ import annotations

from pathlib import Path
import sys


# Add the repo's source folder so this script can import the active instrument API.
REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "source"
sys.path.insert(0, str(SOURCE_DIR))

from instruments import HP4192A  # noqa: E402


# Change this if your VISA resource string is different.
RESOURCE = "TCPIP0::192.168.1.244::gpib0,5::INSTR"

# Set the frequency you want configure() to send to the instrument.
TARGET_FREQUENCY_HZ = 10.4

# VISA timeout in milliseconds.
TIMEOUT_MS = 5000


def main() -> None:
    print("HP 4192A frequency check")
    print("------------------------")
    print(f"Resource: {RESOURCE}")
    print(f"Target frequency: {TARGET_FREQUENCY_HZ} Hz")
    print()

    meter = HP4192A.open(RESOURCE, timeout_ms=TIMEOUT_MS)

    try:
        print("Ping before configure()")
        print("-----------------------")
        meter.ping()

        print()
        print(f"Sending configure(frequency_hz={TARGET_FREQUENCY_HZ})")
        meter.configure(frequency_hz=TARGET_FREQUENCY_HZ)

        print()
        print("Ping after configure()")
        print("----------------------")
        meter.ping()

    finally:
        meter.close()
        print()
        print("Connection closed.")


if __name__ == "__main__":
    main()

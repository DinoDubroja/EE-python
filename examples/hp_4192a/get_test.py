"""
Simple terminal script for one HP 4192A `get()` call.

Purpose
-------
Use this script when you want one current parameter value from the instrument
without running the larger manual test scripts.

How to use
----------
1. Edit `RESOURCE` if needed.
2. Run:

   python examples/hp_4192a/get_test.py

3. Select one parameter by number or by name.
4. The script reads that value from the instrument and exits.
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


PARAMETERS: list[tuple[str, str]] = [
    ("frequency_hz", "Current spot frequency in hertz"),
    ("bias_voltage_v", "Current spot bias in volts"),
    ("osc_level_v", "Current oscillator level in volts"),
    ("display_a", "Current DISPLAY A measurement family"),
    ("display_b", "Current DISPLAY B measurement family"),
    ("circuit_mode", "Current circuit mode when DISPLAY A exposes it"),
]


def prompt_for_parameter() -> str:
    while True:
        print()
        print("Available parameters")
        print("--------------------")
        for index, (name, description) in enumerate(PARAMETERS, start=1):
            print(f"{index}. {name}")
            print(f"   {description}")

        choice = input(
            "\nSelect one parameter by number or by exact name: "
        ).strip()

        if not choice:
            print("Please enter a selection.")
            continue

        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(PARAMETERS):
                return PARAMETERS[index - 1][0]

        for name, _description in PARAMETERS:
            if choice == name:
                return name

        print("Selection not recognized. Try again.")


def main() -> None:
    print("HP 4192A get_test")
    print("-----------------")
    print(f"Resource: {RESOURCE}")

    parameter_name = prompt_for_parameter()

    meter = HP4192A.open(RESOURCE, timeout_ms=TIMEOUT_MS)

    try:
        print()
        print(f'Reading get("{parameter_name}")')
        print("-----------------------------")
        value = meter.get(parameter_name)
        print(f"{parameter_name}: {value}")
    finally:
        meter.close()
        print()
        print("Connection closed.")


if __name__ == "__main__":
    main()

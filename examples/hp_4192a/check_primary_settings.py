"""
Guided hardware check for the first HP 4192A API settings.

Purpose
-------
This script is meant for bench validation, not automated testing.

It goes through a small set of important settings one by one:

- display pair
- spot frequency
- spot bias
- oscillator level

After each step it:

1. sends one `configure(...)` call
2. runs `ping()`
3. pauses so you can compare the printed report with the front panel

How to use
----------
1. Edit RESOURCE if needed.
2. Run:

   python examples/hp_4192a/check_primary_settings.py

3. Follow the prompts.
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


STEPS: list[tuple[str, dict[str, object]]] = [
    (
        "Set display pair to impedance and phase in degrees",
        {
            "display_a": "impedance",
            "display_b": "phase_deg",
        },
    ),
    (
        "Set spot frequency to 1 kHz",
        {
            "frequency_hz": 1_000.0,
        },
    ),
    (
        "Set spot bias to 0.50 V",
        {
            "bias_voltage_v": 0.50,
        },
    ),
    (
        "Set oscillator level to 0.100 V",
        {
            "osc_level_v": 0.100,
        },
    ),
    (
        "Set display pair to inductance and quality factor",
        {
            "display_a": "inductance",
            "display_b": "quality_factor",
        },
    ),
    (
        "Set display pair to capacitance and dissipation factor",
        {
            "display_a": "capacitance",
            "display_b": "dissipation_factor",
        },
    ),
]


def wait_for_user(message: str) -> None:
    input(f"{message}\nPress Enter to continue...")


def run_one_step(
    meter: HP4192A,
    *,
    step_title: str,
    configure_kwargs: dict[str, object],
    index: int,
    total: int,
) -> None:
    print()
    print("=" * 72)
    print(f"Step {index} of {total}")
    print(step_title)
    print("=" * 72)
    print("configure() call:")
    for key, value in configure_kwargs.items():
        print(f"  {key}={value!r}")

    wait_for_user("The script will now send this configure() call to the instrument.")

    meter.configure(**configure_kwargs)

    print()
    print("ping() after configure()")
    print("------------------------")
    meter.ping()

    wait_for_user("Compare the report with the front panel before moving to the next step.")


def main() -> None:
    print("HP 4192A primary-settings check")
    print("-------------------------------")
    print(f"Resource: {RESOURCE}")
    print()
    print("This script checks the first group of high-value settings one by one.")
    print("It is meant for manual bench verification.")

    wait_for_user("Make sure the instrument is connected and safe to reconfigure.")

    meter = HP4192A.open(RESOURCE, timeout_ms=TIMEOUT_MS)

    try:
        print()
        print("Initial ping()")
        print("--------------")
        meter.ping()

        total = len(STEPS)
        for index, (step_title, configure_kwargs) in enumerate(STEPS, start=1):
            run_one_step(
                meter,
                step_title=step_title,
                configure_kwargs=configure_kwargs,
                index=index,
                total=total,
            )
    finally:
        meter.close()
        print()
        print("Connection closed.")


if __name__ == "__main__":
    main()

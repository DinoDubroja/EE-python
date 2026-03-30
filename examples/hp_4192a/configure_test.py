"""
Guided hardware check for the current HP 4192A API.

Purpose
-------
This script is meant for bench validation, not automated testing.

It walks through every high-level setting that is currently implemented in the
HP 4192A driver:

- all supported display-function pairs
- circuit mode
- spot frequency
- spot bias
- oscillator level

After each step it:

1. sends one `configure(...)` call
2. optionally pauses before `ping()` so you can look at DISPLAY C directly
3. runs `ping()`
4. pauses so you can compare the printed report with the front panel

This is the script to use when you want to answer questions like:

- did the driver really change the instrument?
- did `ping()` recall the same state that the front panel shows?
- does DISPLAY C follow the last changed test parameter?

How to use
----------
1. Edit RESOURCE if needed.
2. Run:

   python examples/hp_4192a/configure_test.py

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


STEPS: list[dict[str, object]] = [
    {
        "title": "Set display pair to impedance and phase in degrees",
        "configure_kwargs": {
            "display_a": "impedance",
            "display_b": "phase_deg",
        },
        "checks": [
            "DISPLAY A should show impedance.",
            "DISPLAY B should show phase in degrees.",
        ],
    },
    {
        "title": "Set display pair to impedance and phase in radians",
        "configure_kwargs": {
            "display_a": "impedance",
            "display_b": "phase_rad",
        },
        "checks": [
            "DISPLAY A should still show impedance.",
            "DISPLAY B should now show phase in radians.",
        ],
    },
    {
        "title": "Set spot frequency to 1 kHz",
        "configure_kwargs": {
            "frequency_hz": 1_000.0,
        },
        "checks": [
            "DISPLAY C should show the current spot frequency if the instrument follows the last changed parameter.",
            "ping() should report spot frequency as 1 kHz.",
        ],
    },
    {
        "title": "Set spot bias to +0.50 V",
        "configure_kwargs": {
            "bias_voltage_v": 0.50,
        },
        "checks": [
            "DISPLAY C should show the bias value if the instrument follows the last changed parameter.",
            "ping() should report spot bias as 0.5 V.",
        ],
    },
    {
        "title": "Set spot bias to -0.50 V",
        "configure_kwargs": {
            "bias_voltage_v": -0.50,
        },
        "checks": [
            "Confirm that the negative sign is accepted on the front panel.",
            "ping() should report spot bias as -0.5 V.",
        ],
    },
    {
        "title": "Set oscillator level to 0.100 V",
        "configure_kwargs": {
            "osc_level_v": 0.100,
        },
        "checks": [
            "DISPLAY C should show the oscillator level if the instrument follows the last changed parameter.",
            "ping() should report oscillator level as 0.1 V.",
        ],
    },
    {
        "title": "Set oscillator level to 0.105 V",
        "configure_kwargs": {
            "osc_level_v": 0.105,
        },
        "checks": [
            "This checks the 5 mV resolution region above 0.100 V.",
            "ping() should report oscillator level as 0.105 V.",
        ],
    },
    {
        "title": "Set inductance and quality factor in series mode",
        "configure_kwargs": {
            "circuit_mode": "series",
            "display_a": "inductance",
            "display_b": "quality_factor",
        },
        "checks": [
            "DISPLAY A should show inductance in series mode.",
            "DISPLAY B should show quality factor.",
            "ping() should report circuit mode as series.",
        ],
    },
    {
        "title": "Set inductance and dissipation factor in parallel mode",
        "configure_kwargs": {
            "circuit_mode": "parallel",
            "display_a": "inductance",
            "display_b": "dissipation_factor",
        },
        "checks": [
            "DISPLAY A should show inductance in parallel mode.",
            "DISPLAY B should show dissipation factor.",
            "ping() should report circuit mode as parallel.",
        ],
    },
    {
        "title": "Set capacitance and quality factor in series mode",
        "configure_kwargs": {
            "circuit_mode": "series",
            "display_a": "capacitance",
            "display_b": "quality_factor",
        },
        "checks": [
            "DISPLAY A should show capacitance in series mode.",
            "DISPLAY B should show quality factor.",
            "ping() should report circuit mode as series.",
        ],
    },
    {
        "title": "Set capacitance and dissipation factor in parallel mode",
        "configure_kwargs": {
            "circuit_mode": "parallel",
            "display_a": "capacitance",
            "display_b": "dissipation_factor",
        },
        "checks": [
            "DISPLAY A should show capacitance in parallel mode.",
            "DISPLAY B should show dissipation factor.",
            "ping() should report circuit mode as parallel.",
        ],
    },
    {
        "title": "Set inductance and quality factor with circuit mode auto",
        "configure_kwargs": {
            "circuit_mode": "auto",
            "display_a": "inductance",
            "display_b": "quality_factor",
        },
        "checks": [
            "This checks that configure() accepts the auto circuit-mode command.",
            "Front-panel behavior depends on what interpretation the instrument chooses for the current DUT.",
            "ping() may report series or parallel depending on what DISPLAY A actually returns.",
        ],
    },
]


def wait_for_user(message: str) -> None:
    input(f"{message}\nPress Enter to continue...")


def run_one_step(
    meter: HP4192A,
    *,
    step_title: str,
    configure_kwargs: dict[str, object],
    checks: list[str],
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

    print()
    print("What to check:")
    for check in checks:
        print(f"  - {check}")

    wait_for_user("The script will now send this configure() call to the instrument.")

    meter.configure(**configure_kwargs)

    if any(
        key in configure_kwargs
        for key in ("frequency_hz", "bias_voltage_v", "osc_level_v")
    ):
        wait_for_user(
            "Check DISPLAY C now if you want to see whether the instrument followed the last changed numeric parameter before ping() runs."
        )

    print()
    print("ping() after configure()")
    print("------------------------")
    meter.ping()

    wait_for_user("Compare the report with the front panel before moving to the next step.")


def main() -> None:
    print("HP 4192A configure_test")
    print("-----------------------")
    print(f"Resource: {RESOURCE}")
    print()
    print("This script checks all currently supported HP 4192A settings one by one.")
    print("It is meant for manual bench verification.")

    wait_for_user("Make sure the instrument is connected and safe to reconfigure.")

    meter = HP4192A.open(RESOURCE, timeout_ms=TIMEOUT_MS)

    try:
        print()
        print("Initial ping()")
        print("--------------")
        meter.ping()

        total = len(STEPS)
        for index, step in enumerate(STEPS, start=1):
            run_one_step(
                meter,
                step_title=step["title"],
                configure_kwargs=step["configure_kwargs"],
                checks=step["checks"],
                index=index,
                total=total,
            )
    finally:
        meter.close()
        print()
        print("Connection closed.")


if __name__ == "__main__":
    main()

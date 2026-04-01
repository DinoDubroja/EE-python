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
- bias output enable / disable
- oscillator level
- trigger mode
- measurement mode
- ZY range

After each step it:

1. sends one `configure(...)` call
2. either runs `ping()` or tells you the step must be checked on the front panel
3. pauses so you can compare the result with the instrument

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

RANGE_TEST_BASE_CONFIG = {
    "frequency_hz": 1_000.0,
    "osc_level_v": 0.010,
    "circuit_mode": "series",
    "display_a": "impedance",
    "display_b": "phase_deg",
}


STEPS: list[dict[str, object]] = [
    {
        "title": "Set display pair to impedance and phase in degrees",
        "configure_kwargs": {
            "circuit_mode": "series",
            "display_a": "impedance",
            "display_b": "phase_deg",
        },
        "checks": [
            "DISPLAY A should show impedance.",
            "DISPLAY B should show phase in degrees.",
            "The instrument should be in series interpretation for the Z/Y family.",
        ],
    },
    {
        "title": "Set display pair to impedance and phase in radians",
        "configure_kwargs": {
            "circuit_mode": "series",
            "display_a": "impedance",
            "display_b": "phase_rad",
        },
        "checks": [
            "DISPLAY A should still show impedance.",
            "DISPLAY B should now show phase in radians.",
            "The instrument should still be in series interpretation for the Z/Y family.",
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
        "title": "Turn bias output on with a +1.00 V setpoint",
        "configure_kwargs": {
            "bias_voltage_v": 1.00,
            "bias_enabled": True,
        },
        "checks": [
            "The BIAS ON indicator should be on.",
            "DISPLAY C may still show the bias setpoint depending on the current front-panel state.",
            "configure() should say bias_enabled readback is unavailable because this state is not recalled safely yet.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Turn bias output off while keeping a +1.00 V bias setpoint",
        "configure_kwargs": {
            "bias_voltage_v": 1.00,
            "bias_enabled": False,
        },
        "checks": [
            "The BIAS ON indicator should go off.",
            "This checks that bias output state is separate from bias_voltage_v.",
            "configure() should say bias_enabled readback is unavailable because this state is not recalled safely yet.",
        ],
        "skip_ping": True,
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
        "title": "Set measurement mode to normal",
        "configure_kwargs": {
            "measurement_mode": "normal",
        },
        "checks": [
            "The AVERAGE and HIGH SPEED indicators should both be off.",
            "configure() should report measurement_mode readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set measurement mode to average",
        "configure_kwargs": {
            "measurement_mode": "average",
        },
        "checks": [
            "The AVERAGE indicator should be on.",
            "HIGH SPEED should be off.",
            "configure() should report measurement_mode readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set measurement mode to high_speed",
        "configure_kwargs": {
            "measurement_mode": "high_speed",
        },
        "checks": [
            "The HIGH SPEED indicator should be on.",
            "AVERAGE should be off.",
            "configure() should report measurement_mode readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set trigger mode to internal",
        "configure_kwargs": {
            "trigger_mode": "internal",
        },
        "checks": [
            "The front-panel trigger mode should move to internal.",
            "configure() should report trigger_mode readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set trigger mode to external",
        "configure_kwargs": {
            "trigger_mode": "external",
        },
        "checks": [
            "The front-panel trigger mode should move to external.",
            "This step skips ping() because EX-based readback may not be safe immediately after selecting external trigger.",
            "configure() should report trigger_mode readback unavailable.",
        ],
        "skip_ping": True,
        "cleanup_kwargs": {
            "trigger_mode": "hold",
        },
        "cleanup_message": "The script will now restore trigger_mode='hold' so the next EX-based readback steps stay safe.",
    },
    {
        "title": "Set trigger mode to hold",
        "configure_kwargs": {
            "trigger_mode": "hold",
        },
        "checks": [
            "The front-panel trigger mode should move to hold/manual.",
            "configure() should report trigger_mode readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set ZY range to auto",
        "configure_kwargs": {
            **RANGE_TEST_BASE_CONFIG,
            "zy_range": "auto",
        },
        "checks": [
            "ZY RANGE should move to auto.",
            "configure() should report zy_range readback unavailable.",
            "The readable baseline parameters in this step should still verify successfully.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set ZY range to 1 ohm / 10 S",
        "configure_kwargs": {
            **RANGE_TEST_BASE_CONFIG,
            "zy_range": "1_ohm",
        },
        "checks": [
            "ZY RANGE should move to the 1 ohm / 10 S manual range.",
            "configure() should report zy_range readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set ZY range to 10 ohm / 1 S",
        "configure_kwargs": {
            **RANGE_TEST_BASE_CONFIG,
            "zy_range": "10_ohm",
        },
        "checks": [
            "ZY RANGE should move to the 10 ohm / 1 S manual range.",
            "configure() should report zy_range readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set ZY range to 100 ohm / 100 mS",
        "configure_kwargs": {
            **RANGE_TEST_BASE_CONFIG,
            "zy_range": "100_ohm",
        },
        "checks": [
            "ZY RANGE should move to the 100 ohm / 100 mS manual range.",
            "configure() should report zy_range readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set ZY range to 1 kohm / 10 mS",
        "configure_kwargs": {
            **RANGE_TEST_BASE_CONFIG,
            "zy_range": "1_kohm",
        },
        "checks": [
            "ZY RANGE should move to the 1 kohm / 10 mS manual range.",
            "configure() should report zy_range readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set ZY range to 10 kohm / 1 mS",
        "configure_kwargs": {
            **RANGE_TEST_BASE_CONFIG,
            "zy_range": "10_kohm",
        },
        "checks": [
            "ZY RANGE should move to the 10 kohm / 1 mS manual range.",
            "configure() should report zy_range readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set ZY range to 100 kohm / 100 uS",
        "configure_kwargs": {
            **RANGE_TEST_BASE_CONFIG,
            "zy_range": "100_kohm",
        },
        "checks": [
            "ZY RANGE should move to the 100 kohm / 100 uS manual range.",
            "configure() should report zy_range readback unavailable.",
        ],
        "skip_ping": True,
    },
    {
        "title": "Set ZY range to 1 Mohm / 10 uS",
        "configure_kwargs": {
            **RANGE_TEST_BASE_CONFIG,
            "zy_range": "1_mohm",
        },
        "checks": [
            "ZY RANGE should move to the 1 Mohm / 10 uS manual range.",
            "configure() should report zy_range readback unavailable.",
        ],
        "skip_ping": True,
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
    skip_ping: bool,
    cleanup_kwargs: dict[str, object] | None,
    cleanup_message: str | None,
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

    if skip_ping:
        wait_for_user(
            "This step is meant for front-panel verification. Compare the instrument now before moving on."
        )
    else:
        print()
        print("ping() after configure()")
        print("------------------------")
        meter.ping()

        wait_for_user("Compare the report with the front panel before moving to the next step.")

    if cleanup_kwargs is not None:
        print()
        print("Cleanup")
        print("-------")
        if cleanup_message is not None:
            print(cleanup_message)
        print("cleanup configure() call:")
        for key, value in cleanup_kwargs.items():
            print(f"  {key}={value!r}")
        meter.configure(**cleanup_kwargs)


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
                skip_ping=step.get("skip_ping", False),
                cleanup_kwargs=step.get("cleanup_kwargs"),
                cleanup_message=step.get("cleanup_message"),
                index=index,
                total=total,
            )
    finally:
        meter.close()
        print()
        print("Connection closed.")


if __name__ == "__main__":
    main()

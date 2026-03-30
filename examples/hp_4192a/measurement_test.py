"""
Guided hardware check for the current HP 4192A `measure()` function.

Purpose
-------
This script is for bench validation, not automated testing.

It checks the current `measure()` implementation step by step across all
display modes that are currently supported in the driver.

Current coverage
----------------
1. open-circuit behavior when no actual numeric reading exists
2. impedance and phase in degrees
3. impedance and phase in radians
4. inductance and quality factor in series mode
5. inductance and dissipation factor in parallel mode
6. capacitance and quality factor in series mode
7. capacitance and dissipation factor in parallel mode

This is the script to use when you want to answer questions like:

- does `measure()` return the same quantity the front panel is showing?
- does `measure()` fail cleanly when no actual numeric reading exists?
- do the returned numeric values match the current display setup?

How to use
----------
1. Edit `RESOURCE` if needed.
2. Edit the known-DUT settings below so they match what you are testing.
3. Run:

   python examples/hp_4192a/measurement_test.py

4. Follow the prompts.
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

# Known DUT settings for the measurement checks.
#
# Choose one DUT that gives stable readings in the display modes you want to
# inspect. The same DUT is reused for every known-DUT step below.
KNOWN_DUT_DESCRIPTION = "1 uF capacitor"
KNOWN_DUT_FREQUENCY_HZ = 1_000.0
KNOWN_DUT_OSC_LEVEL_V = 0.1

KNOWN_DUT_COMMON_CONFIG = {
    "frequency_hz": KNOWN_DUT_FREQUENCY_HZ,
    "osc_level_v": KNOWN_DUT_OSC_LEVEL_V,
}


def wait_for_user(message: str) -> None:
    input(f"{message}\nPress Enter to continue...")


def print_measurement(reading) -> None:
    print()
    print("Returned measurement values")
    print("---------------------------")
    print(f"display_a: {reading.display_a}")
    print(f"display_b: {reading.display_b}")


def run_step(
    meter: HP4192A,
    *,
    index: int,
    total: int,
    title: str,
    preparation: str,
    configure_kwargs: dict[str, object],
    checks: list[str],
    expect_measure_error: bool = False,
) -> None:
    print()
    print("=" * 72)
    print(f"Step {index} of {total}")
    print(title)
    print("=" * 72)
    print("What to prepare:")
    print(f"  - {preparation}")
    print()
    print("configure() call:")
    for key, value in configure_kwargs.items():
        print(f"  {key}={value!r}")
    print()
    print("What to check:")
    for check in checks:
        print(f"  - {check}")

    wait_for_user("Prepare the bench state shown above.")

    meter.configure(**configure_kwargs)

    wait_for_user(
        "The instrument is configured. Look at the front panel now before ping() and measure() run."
    )

    print()
    print("ping() after configure()")
    print("------------------------")
    meter.ping()

    wait_for_user("Compare the ping() report with the front panel before measure() runs.")

    print()
    print("measure() result")
    print("----------------")
    try:
        reading = meter.measure()
    except Exception as exc:
        if not expect_measure_error:
            raise

        print(f"measure() raised: {exc}")
    else:
        if expect_measure_error:
            raise RuntimeError(
                "measure() returned numeric values, but this step expected it to fail"
            )

        print_measurement(reading)

    wait_for_user("Compare the returned data with the front panel before continuing.")


def main() -> None:
    steps = [
        {
            "title": "Open input: measure() should fail because there is no actual reading",
            "preparation": "Leave the measurement input open with no DUT connected.",
            "configure_kwargs": {
                **KNOWN_DUT_COMMON_CONFIG,
                "circuit_mode": "series",
                "display_a": "impedance",
                "display_b": "phase_deg",
            },
            "checks": [
                "The instrument should be in an open-circuit condition.",
                "measure() should raise an error instead of returning fake numeric values.",
            ],
            "expect_measure_error": True,
        },
        {
            "title": "Known DUT: impedance and phase in degrees",
            "preparation": f"Connect the known DUT: {KNOWN_DUT_DESCRIPTION}.",
            "configure_kwargs": {
                **KNOWN_DUT_COMMON_CONFIG,
                "circuit_mode": "series",
                "display_a": "impedance",
                "display_b": "phase_deg",
            },
            "checks": [
                "DISPLAY A and DISPLAY B should match the configured measurement mode.",
                "measure() should return two numeric values only.",
                "The numeric values should be plausible for the connected DUT.",
            ],
            "expect_measure_error": False,
        },
        {
            "title": "Known DUT: impedance and phase in radians",
            "preparation": f"Keep the same DUT connected: {KNOWN_DUT_DESCRIPTION}.",
            "configure_kwargs": {
                **KNOWN_DUT_COMMON_CONFIG,
                "circuit_mode": "series",
                "display_a": "impedance",
                "display_b": "phase_rad",
            },
            "checks": [
                "DISPLAY A should show impedance.",
                "DISPLAY B should show phase in radians.",
                "measure() should now return impedance/radian-phase data for the same DUT.",
            ],
            "expect_measure_error": False,
        },
        {
            "title": "Known DUT: inductance and quality factor in series mode",
            "preparation": f"Keep the same DUT connected: {KNOWN_DUT_DESCRIPTION}.",
            "configure_kwargs": {
                **KNOWN_DUT_COMMON_CONFIG,
                "circuit_mode": "series",
                "display_a": "inductance",
                "display_b": "quality_factor",
            },
            "checks": [
                "DISPLAY A should show inductance in series mode.",
                "DISPLAY B should show quality factor.",
                "measure() should return two numeric values for the current display pair.",
            ],
            "expect_measure_error": False,
        },
        {
            "title": "Known DUT: inductance and dissipation factor in parallel mode",
            "preparation": f"Keep the same DUT connected: {KNOWN_DUT_DESCRIPTION}.",
            "configure_kwargs": {
                **KNOWN_DUT_COMMON_CONFIG,
                "circuit_mode": "parallel",
                "display_a": "inductance",
                "display_b": "dissipation_factor",
            },
            "checks": [
                "DISPLAY A should show inductance in parallel mode.",
                "DISPLAY B should show dissipation factor.",
                "measure() should return two numeric values for the current display pair.",
            ],
            "expect_measure_error": False,
        },
        {
            "title": "Known DUT: capacitance and quality factor in series mode",
            "preparation": f"Keep the same DUT connected: {KNOWN_DUT_DESCRIPTION}.",
            "configure_kwargs": {
                **KNOWN_DUT_COMMON_CONFIG,
                "circuit_mode": "series",
                "display_a": "capacitance",
                "display_b": "quality_factor",
            },
            "checks": [
                "DISPLAY A should show capacitance in series mode.",
                "DISPLAY B should show quality factor.",
                "measure() should return two numeric values for the current display pair.",
            ],
            "expect_measure_error": False,
        },
        {
            "title": "Known DUT: capacitance and dissipation factor in parallel mode",
            "preparation": f"Keep the same DUT connected: {KNOWN_DUT_DESCRIPTION}.",
            "configure_kwargs": {
                **KNOWN_DUT_COMMON_CONFIG,
                "circuit_mode": "parallel",
                "display_a": "capacitance",
                "display_b": "dissipation_factor",
            },
            "checks": [
                "DISPLAY A should show capacitance in parallel mode.",
                "DISPLAY B should show dissipation factor.",
                "measure() should return two numeric values for the current display pair.",
            ],
            "expect_measure_error": False,
        },
    ]

    print("HP 4192A measurement_test")
    print("-------------------------")
    print(f"Resource: {RESOURCE}")
    print()
    print("This script checks the current measure() implementation step by step.")

    wait_for_user("Make sure the instrument is connected and safe to reconfigure.")

    meter = HP4192A.open(RESOURCE, timeout_ms=TIMEOUT_MS)

    try:
        total = len(steps)
        for index, step in enumerate(steps, start=1):
            run_step(
                meter,
                index=index,
                total=total,
                title=step["title"],
                preparation=step["preparation"],
                configure_kwargs=step["configure_kwargs"],
                checks=step["checks"],
                expect_measure_error=step["expect_measure_error"],
            )
    finally:
        meter.close()
        print()
        print("Connection closed.")


if __name__ == "__main__":
    main()

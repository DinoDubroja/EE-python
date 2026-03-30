"""
Automatic HP 4192A API self-test.

Purpose
-------
This script is a short automatic confidence check for the current HP 4192A
driver. It is meant to run without repeated Enter prompts.

What it checks
--------------
Core block:
- `configure()` across the currently supported settings
- `get()` for exact single-parameter readback
- `ping(show=False)` for readable state reporting

Optional measurement block:
- a few representative `measure()` checks on a known connected DUT

How to use
----------
1. Edit `RESOURCE` if needed.
2. If you want `measure()` included, set `RUN_MEASUREMENT_BLOCK = True` and
   connect the known DUT before starting the script.
3. Run:

   python examples/hp_4192a/self_test.py

The script prints progress as it goes, then prints a final pass/fail summary.
"""

from __future__ import annotations

from pathlib import Path
import math
import sys
import time


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "source"
sys.path.insert(0, str(SOURCE_DIR))

from instruments import HP4192A  # noqa: E402


RESOURCE = "TCPIP0::192.168.1.244::gpib0,5::INSTR"
TIMEOUT_MS = 5000

# Keep this off by default so the script stays safe when no DUT is connected.
RUN_MEASUREMENT_BLOCK = False

# Known-DUT settings used only when RUN_MEASUREMENT_BLOCK is True.
KNOWN_DUT_DESCRIPTION = "1 uF capacitor"
KNOWN_DUT_FREQUENCY_HZ = 1_000.0
KNOWN_DUT_OSC_LEVEL_V = 0.1


CORE_STEPS: list[dict[str, object]] = [
    {
        "title": "Impedance and phase in degrees at 1 kHz",
        "configure_kwargs": {
            "frequency_hz": 1_000.0,
            "circuit_mode": "series",
            "display_a": "impedance",
            "display_b": "phase_deg",
        },
        "get_checks": {
            "frequency_hz": 1_000.0,
            "display_a": "impedance",
            "display_b": "phase_deg",
            "circuit_mode": "series",
        },
        "ping_checks": {
            "spot frequency": "1 kHz",
            "display A": "impedance",
            "display B": "phase (deg)",
            "circuit mode": "series",
        },
    },
    {
        "title": "Impedance and phase in radians at 10 kHz",
        "configure_kwargs": {
            "frequency_hz": 10_000.0,
            "circuit_mode": "series",
            "display_a": "impedance",
            "display_b": "phase_rad",
        },
        "get_checks": {
            "frequency_hz": 10_000.0,
            "display_a": "impedance",
            "display_b": "phase_rad",
            "circuit_mode": "series",
        },
        "ping_checks": {
            "spot frequency": "10 kHz",
            "display A": "impedance",
            "display B": "phase (rad)",
            "circuit mode": "series",
        },
    },
    {
        "title": "Positive spot bias",
        "configure_kwargs": {
            "bias_voltage_v": 0.50,
        },
        "get_checks": {
            "bias_voltage_v": 0.50,
        },
        "ping_checks": {
            "spot bias": "0.5 V",
        },
    },
    {
        "title": "Negative spot bias",
        "configure_kwargs": {
            "bias_voltage_v": -0.50,
        },
        "get_checks": {
            "bias_voltage_v": -0.50,
        },
        "ping_checks": {
            "spot bias": "-0.5 V",
        },
    },
    {
        "title": "Oscillator level at 0.100 V",
        "configure_kwargs": {
            "osc_level_v": 0.100,
        },
        "get_checks": {
            "osc_level_v": 0.100,
        },
        "ping_checks": {
            "oscillator level": "0.1 V",
        },
    },
    {
        "title": "Oscillator level at 0.105 V",
        "configure_kwargs": {
            "osc_level_v": 0.105,
        },
        "get_checks": {
            "osc_level_v": 0.105,
        },
        "ping_checks": {
            "oscillator level": "0.105 V",
        },
    },
    {
        "title": "Inductance and quality factor in series mode",
        "configure_kwargs": {
            "circuit_mode": "series",
            "display_a": "inductance",
            "display_b": "quality_factor",
        },
        "get_checks": {
            "display_a": "inductance",
            "display_b": "quality_factor",
            "circuit_mode": "series",
        },
        "ping_checks": {
            "display A": "inductance (series)",
            "display B": "quality factor",
            "circuit mode": "series",
        },
    },
    {
        "title": "Inductance and dissipation factor in parallel mode",
        "configure_kwargs": {
            "circuit_mode": "parallel",
            "display_a": "inductance",
            "display_b": "dissipation_factor",
        },
        "get_checks": {
            "display_a": "inductance",
            "display_b": "dissipation_factor",
            "circuit_mode": "parallel",
        },
        "ping_checks": {
            "display A": "inductance (parallel)",
            "display B": "dissipation factor",
            "circuit mode": "parallel",
        },
    },
    {
        "title": "Capacitance and quality factor in series mode",
        "configure_kwargs": {
            "circuit_mode": "series",
            "display_a": "capacitance",
            "display_b": "quality_factor",
        },
        "get_checks": {
            "display_a": "capacitance",
            "display_b": "quality_factor",
            "circuit_mode": "series",
        },
        "ping_checks": {
            "display A": "capacitance (series)",
            "display B": "quality factor",
            "circuit mode": "series",
        },
    },
    {
        "title": "Capacitance and dissipation factor in parallel mode",
        "configure_kwargs": {
            "circuit_mode": "parallel",
            "display_a": "capacitance",
            "display_b": "dissipation_factor",
        },
        "get_checks": {
            "display_a": "capacitance",
            "display_b": "dissipation_factor",
            "circuit_mode": "parallel",
        },
        "ping_checks": {
            "display A": "capacitance (parallel)",
            "display B": "dissipation factor",
            "circuit mode": "parallel",
        },
    },
]


MEASUREMENT_STEPS: list[dict[str, object]] = [
    {
        "title": "Known DUT in capacitance and dissipation-factor mode",
        "configure_kwargs": {
            "frequency_hz": KNOWN_DUT_FREQUENCY_HZ,
            "osc_level_v": KNOWN_DUT_OSC_LEVEL_V,
            "circuit_mode": "parallel",
            "display_a": "capacitance",
            "display_b": "dissipation_factor",
        },
    },
    {
        "title": "Known DUT in impedance and phase-degree mode",
        "configure_kwargs": {
            "frequency_hz": KNOWN_DUT_FREQUENCY_HZ,
            "osc_level_v": KNOWN_DUT_OSC_LEVEL_V,
            "circuit_mode": "series",
            "display_a": "impedance",
            "display_b": "phase_deg",
        },
    },
    {
        "title": "Known DUT in impedance and phase-radian mode",
        "configure_kwargs": {
            "frequency_hz": KNOWN_DUT_FREQUENCY_HZ,
            "osc_level_v": KNOWN_DUT_OSC_LEVEL_V,
            "circuit_mode": "series",
            "display_a": "impedance",
            "display_b": "phase_rad",
        },
    },
]


def extract_state_rows(report) -> dict[str, object]:
    for title, rows in report.sections:
        if title == "State":
            return rows
    return {}


def verify_get_value(parameter_name: str, actual: object, expected: object) -> None:
    if isinstance(expected, float):
        if not isinstance(actual, (int, float)) or not math.isclose(
            float(actual),
            expected,
            rel_tol=0.0,
            abs_tol=1e-9,
        ):
            raise AssertionError(
                f'get("{parameter_name}") returned {actual!r}, expected {expected!r}'
            )
    elif actual != expected:
        raise AssertionError(
            f'get("{parameter_name}") returned {actual!r}, expected {expected!r}'
        )


def verify_ping_value(state_rows: dict[str, object], key: str, expected: str) -> None:
    actual = state_rows.get(key)
    if actual is None:
        raise AssertionError(f'ping() did not report "{key}"')
    if str(actual) != expected:
        raise AssertionError(f'ping() reported {key!r} as {actual!r}, expected {expected!r}')


def run_core_step(meter: HP4192A, step: dict[str, object], index: int, total: int) -> None:
    print()
    print("=" * 72)
    print(f"Core step {index} of {total}")
    print(step["title"])
    print("=" * 72)

    configure_kwargs = step["configure_kwargs"]
    print("configure() call:")
    for key, value in configure_kwargs.items():
        print(f"  {key}={value!r}")

    meter.configure(**configure_kwargs)

    get_checks = step["get_checks"]
    if get_checks:
        print("get() checks:")
        for parameter_name, expected_value in get_checks.items():
            actual_value = meter.get(parameter_name)
            verify_get_value(parameter_name, actual_value, expected_value)
            print(f'  {parameter_name}: {actual_value}')

    ping_checks = step["ping_checks"]
    if ping_checks:
        print("ping() checks:")
        report = meter.ping(show=False)
        state_rows = extract_state_rows(report)
        for key, expected_value in ping_checks.items():
            verify_ping_value(state_rows, key, expected_value)
            print(f"  {key}: {state_rows[key]}")

    print("Result: PASS")


def run_measurement_step(
    meter: HP4192A,
    step: dict[str, object],
    index: int,
    total: int,
) -> None:
    print()
    print("=" * 72)
    print(f"Measurement step {index} of {total}")
    print(step["title"])
    print("=" * 72)

    configure_kwargs = step["configure_kwargs"]
    print("configure() call:")
    for key, value in configure_kwargs.items():
        print(f"  {key}={value!r}")

    meter.configure(**configure_kwargs)
    reading = meter.measure()

    if not math.isfinite(reading.display_a) or not math.isfinite(reading.display_b):
        raise AssertionError("measure() returned a non-finite value")

    print(f"  measure().display_a: {reading.display_a}")
    print(f"  measure().display_b: {reading.display_b}")
    print("Result: PASS")


def main() -> None:
    print("HP 4192A self_test")
    print("-------------------")
    print(f"Resource: {RESOURCE}")
    if RUN_MEASUREMENT_BLOCK:
        print(f"Measurement block: enabled ({KNOWN_DUT_DESCRIPTION})")
    else:
        print("Measurement block: skipped")

    started_at = time.monotonic()
    failures: list[str] = []

    meter = HP4192A.open(RESOURCE, timeout_ms=TIMEOUT_MS)

    try:
        for index, step in enumerate(CORE_STEPS, start=1):
            try:
                run_core_step(meter, step, index, len(CORE_STEPS))
            except Exception as exc:
                failures.append(f'Core step {index}: {step["title"]} -> {exc}')
                print(f"Result: FAIL ({exc})")

        if RUN_MEASUREMENT_BLOCK:
            print()
            print(f"Running measurement block for DUT: {KNOWN_DUT_DESCRIPTION}")
            for index, step in enumerate(MEASUREMENT_STEPS, start=1):
                try:
                    run_measurement_step(
                        meter,
                        step,
                        index,
                        len(MEASUREMENT_STEPS),
                    )
                except Exception as exc:
                    failures.append(
                        f'Measurement step {index}: {step["title"]} -> {exc}'
                    )
                    print(f"Result: FAIL ({exc})")
        else:
            print()
            print("Measurement block skipped.")
            print("Set RUN_MEASUREMENT_BLOCK = True when a known DUT is connected.")
    finally:
        meter.close()

    elapsed_s = time.monotonic() - started_at

    print()
    print("=" * 72)
    print("Summary")
    print("=" * 72)
    if failures:
        print(f"Self-test finished with {len(failures)} failure(s) in {elapsed_s:.1f} s.")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print(f"Self-test passed in {elapsed_s:.1f} s.")


if __name__ == "__main__":
    main()

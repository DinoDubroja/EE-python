# Instrument API Standard

This document captures the default design pattern for instrument APIs in this
repo.

The goal is simple:

- keep the interface easy to use at the bench
- use the same mental model across instruments
- keep code readable and documentation close to the code

## Core Rule

Use high-level electrical-engineering names, not raw command codes.

Good:

```python
meter.configure(
    frequency_hz=1_000,
    bias_voltage_v=0.5,
    display_a="impedance",
    display_b="phase_deg",
)
```

Bad:

```python
meter.write("FR1EN")
meter.write("A1")
meter.write("B1")
```

Raw SCPI or HP-IB codes still belong in the instrument command guide.

## Required Public Methods

Every instrument should implement:

- `ping()`
- `get()`
- `configure()`

Some instruments should also implement:

- `measure()`

## Meaning Of Each Method

`ping()`

- readable diagnostic report
- meant for a human operator
- should show current instrument state
- should only report values actually read from the instrument

`get(parameter_name)`

- return one current parameter value
- no extra report text
- use this when code needs one value, not a full report

`configure(...)`

- one high-level entry point for changing instrument state
- change only the parameters that were explicitly passed
- avoid many tiny public helper functions for ordinary setup

`measure()`

- higher-level data-read function
- return only actual measurement data
- do not mix measurement data with diagnostic/status data
- if there is no valid measurement, raise an error

## Configure Rules

`configure()` should do a self-check when possible.

That means:

- send the requested command(s)
- read the changed parameter(s) back silently
- compare requested vs actual
- print one short uniform confirmation line per changed parameter

Behavior:

- exact match: print success
- rounded/clamped by instrument: print requested and actual value
- no safe readback path: print `readback unavailable`
- true mismatch: raise an error

Do not guess state from cached Python values and present that as instrument
readback.

## Readback Rule

If the instrument does not provide a proven safe recall path for a parameter:

- do not put it in `get()`
- do not report it in `ping()`
- it may still be supported in `configure()`
- document clearly that it is configure-only for now

## Documentation Rules

Public methods need real instrument-specific docstrings.

When hovering over `configure()`, the user should be able to see:

- supported parameter names
- accepted values
- units
- valid ranges
- what the parameter changes on the instrument

Also required for each instrument:

- one command guide markdown file

That command guide should explain:

- command style used by the instrument
- raw command mapping for implemented features
- examples
- known safety warnings
- what is settable
- what is safely recallable

## Function Signature Style

Keep `configure()` flat, but group parameters in logical blocks.

Example:

```python
def configure(
    self,
    *,
    # Test signal
    frequency_hz: float | None = None,
    osc_level_v: float | None = None,
    # Trigger and acquisition
    trigger_mode: str | None = None,
    measurement_mode: str | None = None,
    # Measurement display
    display_a: str | None = None,
    display_b: str | None = None,
) -> None:
    ...
```

This keeps one entry point while staying readable.

## Example Scripts

Each instrument should keep the same example/test pattern when relevant:

- `configure_test.py`
- `measurement_test.py`
- `get_test.py`
- `self_test.py`

Meaning:

- `configure_test.py`: guided manual bench check
- `measurement_test.py`: guided manual measurement check
- `get_test.py`: one-shot terminal helper for a single `get()`
- `self_test.py`: automatic short confidence check

Rule:

- manual-only settings may appear in `configure_test.py`
- `self_test.py` should only automatically verify what the instrument can
  actually read back safely

## Driver Layer Vs Application Layer

Instrument driver layer:

- spot settings
- current state
- one current measurement

Application layer:

- sweeps
- CSV export
- plotting
- combined measurement procedures

Example:

- `frequency_hz` belongs in the instrument API
- `start`, `stop`, `points_per_decade`, CSV output, and PNG output belong in a
  sweep application script

## Naming Rule

Keep names simple and field-oriented.

Prefer:

- `source`
- `instruments`
- `examples`
- `scripts`
- `archive`

Avoid software-heavy names when a plain EE name is clearer.

## Final Rule

Do not implement uncertain commands by guessing.

When the manual is ambiguous:

- re-read the manual
- test on hardware
- update the command guide
- ask before locking in a questionable interpretation

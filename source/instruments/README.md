# Instruments

This folder contains the active instrument APIs.

## Naming

- `instrument.py`: common instrument/report structure shared by every instrument.
- `visa.py`: PyVISA connection code.
- `hp_4192a.py`: HP 4192A impedance-analyzer API.
- `hp_4192a_commands.md`: working command reference for the HP 4192A.

## Default Rule For This Repo

Every instrument should have:

- a Python API file
- a command-reference document written for bench use

The command-reference document should explain the instrument's command style in
plain language:

- SCPI commands for SCPI instruments
- HP-IB / GPIB remote program codes for older instruments
- examples for common tasks
- warnings about commands that are not safe to treat as read-only

## Style

Each instrument should at least provide:

- `ping()`
- `get()`
- `configure()`

Other instrument-specific functions should be added only when they are actually needed.

When an instrument has `measure()`, it should be the higher-level data-read
entry point:

- return structured measurement data
- avoid printing by default
- use a readable return type instead of a raw string when possible
- document exactly what data fields are returned

`configure()` should not only send commands. When the instrument offers a safe
readback path, it should also:

- read the changed parameter back from the instrument
- print one short confirmation line in a uniform format
- raise an error if the readback disagrees with the requested change
- report `readback unavailable` instead of guessing when the parameter cannot
  be verified safely

## HP 4192A Notes

The 4192A is not SCPI-based. It uses older HP-IB remote program codes.

Current implementation scope is intentionally small:

- `ping()` reads the current display functions, inferred circuit mode, spot
  frequency, spot bias, and oscillator level from the instrument
- `get(parameter_name)` currently supports:
  - `frequency_hz`
  - `bias_voltage_v`
  - `osc_level_v`
  - `display_a`
  - `display_b`
  - `circuit_mode`
- `configure(...)` currently supports:
  - `frequency_hz`
  - `bias_voltage_v`
  - `osc_level_v`
  - `circuit_mode`
  - `display_a`
  - `display_b`
- `measure()` returns one current DISPLAY A/B numeric measurement pair using
  the instrument's present display setup

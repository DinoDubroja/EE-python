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
- `configure()`

Other instrument-specific functions should be added only when they are actually needed.

## HP 4192A Notes

The 4192A is not SCPI-based. It uses older HP-IB remote program codes.

Current implementation scope is intentionally small:

- `ping()` reads the current display functions and spot frequency from the
  instrument
- `configure(...)` currently supports:
  - `frequency_hz`
  - `bias_voltage_v`
  - `osc_level_v`
  - `display_a`
  - `display_b`

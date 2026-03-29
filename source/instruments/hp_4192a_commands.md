# HP 4192A Command Guide

This document is the working command reference for the HP 4192A in this repo.

The goal is simple:

- explain the remote command style of the instrument
- show which commands are useful for normal work
- give examples you can copy without reopening the manual

This instrument is not SCPI. It uses older HP-IB remote program codes.

## Current High-Level API Keywords

The current Python API exposes these high-level `configure()` keywords:

- `frequency_hz`
- `bias_voltage_v`
- `osc_level_v`
- `display_a`
- `display_b`

The current `ping()` implementation reads back:

- current DISPLAY A function
- current DISPLAY B function
- circuit mode when it can be inferred from DISPLAY A
- spot frequency

The sections below explain exactly which raw HP-IB codes are used for each of
those high-level keywords.

## First Rule

Do not treat all bus operations as harmless.

In this lab setup, sending a VISA device clear changed the front-panel
frequency back to `100 kHz`. Because of that:

- `ping()` must not use device clear
- read-only checks should avoid `clear()`
- if a command path changes the front panel unexpectedly, stop and test that
  command path directly before building it into the API

## Manual Sections That Matter

These are the manual sections that the current driver work is based on:

- Table `3-23`: remote program codes used for control, recall, trigger, output
  format, sweep mode, range, and similar instrument actions
- Table `3-24`: program codes for parameter setting
- Paragraph `3-124`: parameter-setting format and units
- Figure `3-36`: output data format when the instrument returns A/B or A/B/C
  data
- Table `3-25`: output data codes
- Figure `3-38`: sample spot-measurement program

## Two Command Families

The manual separates commands into two groups. This distinction matters.

### 1. Control and Recall Codes

These come from table `3-23`.

Examples:

- `F1`: output format is `DISPLAY A/B/C`
- `F0`: output format is `DISPLAY A/B`
- `FRR`: recall the current spot-frequency parameter
- `T1`: trigger mode `INT`
- `T2`: trigger mode `EXT`
- `T3`: trigger mode `HOLD/MANUAL`
- `EX`: execute / trigger the instrument

These are not the numeric parameter-setting commands.

### 2. Parameter-Setting Codes

These come from table `3-24`.

Examples:

- `FR...EN`: set spot frequency
- `TF...EN`: set start frequency
- `PF...EN`: set stop frequency
- `SF...EN`: set step frequency
- `BI...EN`: set spot bias
- `TB...EN`: set start bias
- `PB...EN`: set stop bias
- `SB...EN`: set step bias
- `OL...EN`: set oscillator level
- `RA...EN`: set reference A
- `RB...EN`: set reference B

These commands carry a numeric value and end with `EN`.

## Parameter-Setting Format

Paragraph `3-124` describes the format as:

```text
XX+/-NNNN.NNNNEN
```

Practical meaning:

- `XX` is the parameter code, for example `FR`
- the number is the value
- `EN` is the terminator for the parameter entry

For frequency-related parameters, the unit is `kHz`.

Examples:

- `FR10EN` sets spot frequency to `10 kHz`
- `FR1EN` sets spot frequency to `1 kHz`
- `FR0.005EN` sets spot frequency to `5 Hz`
- `TF100EN` sets start frequency to `100 kHz`
- `PF1000EN` sets stop frequency to `1 MHz`

## Frequency Commands

`frequency_hz` in the Python API maps to the spot-frequency commands below.

### Set Spot Frequency

Use table `3-24` code `FR` with a numeric value in `kHz`, then end with `EN`.

Examples:

- `FR1EN` -> `1 kHz`
- `FR10EN` -> `10 kHz`
- `FR100EN` -> `100 kHz`
- `FR0.010EN` -> `10 Hz`

### Recall Spot Frequency for Output

Use table `3-23` code:

- `FRR`

This is not the set command. It is the recall-side command for the current
spot-frequency parameter.

### High-Level Mapping

Python keyword:

```python
meter.configure(frequency_hz=1_000)
```

Raw HP-IB command sent by the driver:

```text
FR1EN
```

Python readback path currently used by `ping()`:

```text
F1
FRR
EX
READ
```

### Trigger Output

Use:

- `EX`

`EX` triggers the instrument. When the output format is set to include
DISPLAY C, this allows the current recalled parameter to be sent out.

### Include DISPLAY C in Output

Use:

- `F1`

This tells the instrument to output `DISPLAY A`, `DISPLAY B`, and
`DISPLAY C`.

## How The Current Driver Reads Frequency

The current driver uses this non-destructive sequence:

```text
F1
FRR
EX
READ
```

Meaning:

- `F1` tells the instrument to include DISPLAY C in the output
- `FRR` tells the instrument that the parameter of interest is spot frequency
- `EX` causes the instrument to output the current data string
- the final field in the returned string is DISPLAY C

From figure `3-36`, DISPLAY C contains:

- a unit code
- a numeric value

From table `3-25`, DISPLAY C unit code:

- `K` means `kHz`
- `V` means `V`
- `A` means `mA`
- `R` means reference data

For spot-frequency recall, the returned DISPLAY C field should look like:

```text
K10
```

or

```text
K1.000
```

which means the DISPLAY C value is in `kHz`.

## Spot Bias Commands

`bias_voltage_v` in the Python API maps to the spot-bias commands below.

### Set Spot Bias

Use table `3-24` code `BI` with a numeric value in `V`, then end with `EN`.

Examples:

- `BI0.50EN` -> `+0.50 V`
- `BI-1.00EN` -> `-1.00 V`
- `BI10.00EN` -> `+10.00 V`

Manual limits from table `3-24`:

- range: `-35.00 V` to `+35.00 V`
- resolution: `0.01 V`

### Recall Spot Bias for Output

Use table `3-23` code:

- `BIR`

### High-Level Mapping

Python keyword:

```python
meter.configure(bias_voltage_v=0.5)
```

Raw HP-IB command sent by the driver:

```text
BI0.50EN
```

Candidate readback path to verify on hardware:

```text
F1
BIR
EX
READ
```

Expected DISPLAY C meaning:

- voltage value in volts

Important note:

The scanned manual OCR is inconsistent about the DISPLAY C unit code for
voltage. The driver accepts both `V` and `Y` on readback to stay robust
against that ambiguity while testing on real hardware.

## Oscillator Level Commands

`osc_level_v` in the Python API maps to the oscillator-level commands below.

### Set Oscillator Level

Use table `3-24` code `OL` with a numeric value in `V`, then end with `EN`.

Examples:

- `OL0.010EN` -> `10 mV`
- `OL0.100EN` -> `100 mV`
- `OL0.105EN` -> `105 mV`

Manual limits from table `3-24`:

- range: `0.005 V` to `1.100 V`
- resolution: `0.001 V` from `0.005 V` to `0.100 V`
- resolution: `0.005 V` above `0.100 V` up to `1.100 V`

### Recall Oscillator Level for Output

Use table `3-23` code:

- `OLR`

### High-Level Mapping

Python keyword:

```python
meter.configure(osc_level_v=0.1)
```

Raw HP-IB command sent by the driver:

```text
OL0.100EN
```

Candidate readback path to verify on hardware:

```text
F1
OLR
EX
READ
```

Expected DISPLAY C meaning:

- voltage value in volts

## Display Function Commands

The current driver supports a small, explicit set of measurement-display pairs.
This is intentional. It is better to support a few combinations correctly than
to guess the full table.

### Raw Set Codes from Table 3-23

- `A1`: `Z/Y`
- `A3`: `L`
- `A4`: `C`
- `B1`: first valid DISPLAY B partner for the current DISPLAY A function
- `B2`: second valid DISPLAY B partner for the current DISPLAY A function

### Current High-Level Display Pairs

Supported Python combinations:

- `display_a="impedance"`, `display_b="phase_deg"` -> `A1`, `B1`
- `display_a="impedance"`, `display_b="phase_rad"` -> `A1`, `B2`
- `display_a="inductance"`, `display_b="quality_factor"` -> `A3`, `B1`
- `display_a="inductance"`, `display_b="dissipation_factor"` -> `A3`, `B2`
- `display_a="capacitance"`, `display_b="quality_factor"` -> `A4`, `B1`
- `display_a="capacitance"`, `display_b="dissipation_factor"` -> `A4`, `B2`

### High-Level Mapping

Python call:

```python
meter.configure(display_a="inductance", display_b="quality_factor")
```

Raw HP-IB commands sent by the driver:

```text
A3
B1
```

### How `ping()` Reads Display Functions

`ping()` does not use a separate display-function recall code. Instead it reads
the function codes already present in the DISPLAY A and DISPLAY B parts of the
measurement output string.

Current readback path:

```text
F1
FRR
EX
READ
```

This gives the driver:

- DISPLAY A function code
- DISPLAY B function code
- DISPLAY C spot-frequency value

### DISPLAY A Readback Codes Used by the Driver

From table `3-25`, the driver currently interprets these DISPLAY A codes:

- `ZF` -> impedance
- `LS` -> inductance (series)
- `LP` -> inductance (parallel)
- `CS` -> capacitance (series)
- `CP` -> capacitance (parallel)

### DISPLAY B Readback Codes Used by the Driver

From table `3-25`, the driver currently interprets these DISPLAY B codes:

- `TD` -> phase (deg)
- `TR` -> phase (rad)
- `QF` -> quality factor
- `DF` -> dissipation factor

### Circuit Mode Inference

The driver does not currently send a circuit-mode recall code because table
`3-23` does not provide one in the same style as `FRR`, `BIR`, or `OLR`.

What the driver does instead:

- if DISPLAY A reads back as `LS` or `CS`, `ping()` reports `series`
- if DISPLAY A reads back as `LP` or `CP`, `ping()` reports `parallel`

That means circuit mode is only reported when it can be inferred from the
current DISPLAY A function.

## How The Current Driver Sets Frequency

The current driver uses:

```text
FR<value in kHz>EN
```

Examples:

- `FR1EN`
- `FR10EN`
- `FR100EN`

This is based on table `3-24` and figure `3-38`.

## Working Bench Examples

### Example 1: Read Current Spot Frequency

```text
F1
FRR
EX
READ
```

If DISPLAY C comes back as `K10`, the instrument spot frequency is `10 kHz`.

### Example 2: Set Spot Frequency to 1 kHz

```text
FR1EN
```

The front panel should move to `1 kHz`.

### Example 3: Set Spot Frequency to 10 kHz and Read It Back

```text
FR10EN
F1
FRR
EX
READ
```

Expected DISPLAY C value:

```text
K10
```

### Example 4: Spot Measurement Style Sequence from the Manual

The sample program in figure `3-38` uses this kind of flow:

```text
A1B1T3 F1
FR10EN
EX
READ
```

Practical meaning:

- choose display functions
- use hold/manual trigger
- include DISPLAY C in output
- set frequency to `10 kHz`
- trigger
- read returned data

## Common Control / Recall Codes

These are the codes from table `3-23` that are most likely to matter in
normal use.

### Output Format

- `F0`: output `DISPLAY A/B`
- `F1`: output `DISPLAY A/B/C`

### Trigger

- `T1`: internal trigger mode
- `T2`: external trigger mode
- `T3`: hold/manual trigger mode
- `EX`: execute trigger

Important note:

- the `T1`, `T2`, and `T3` codes select trigger mode
- they do not themselves trigger the instrument
- `EX` is the trigger action

### Sweep

- `W0`: manual sweep mode
- `W1`: auto sweep mode
- `W2`: step up in manual sweep, or start up in auto sweep
- `W3`: pause in auto sweep
- `W4`: step down in manual sweep, or start down in auto sweep
- `AB`: sweep abort
- `G0`: log sweep off
- `G1`: log sweep on

### Circuit Mode

- `C1`: auto
- `C2`: series
- `C3`: parallel

### Z/Y Range

- `R1` to `R7`: fixed ranges
- `R8`: auto range

### Data Ready

- `D0`: data ready SRQ off
- `D1`: data ready SRQ on

### Parameter Recall Codes

- `FRR`: recall spot frequency
- `SFR`: recall step frequency
- `TFR`: recall start frequency
- `PFR`: recall stop frequency
- `BIR`: recall spot bias
- `SBR`: recall step bias
- `TBR`: recall start bias
- `PBR`: recall stop bias
- `OLR`: recall oscillator level
- `RAR`: recall reference A
- `RBR`: recall reference B

### Save / Recall Instrument Key Status

- `SA0` to `SA4`: save front-panel key status into memory location `0` to `4`
- `RC0` to `RC4`: recall front-panel key status from memory location `0` to `4`

## Parameter-Setting Codes

These come from table `3-24`.

### Frequency Parameters

- `FR`: spot frequency
- `TF`: start frequency
- `PF`: stop frequency
- `SF`: step frequency

Frequency unit: `kHz`

### Bias Parameters

- `BI`: spot bias
- `TB`: start bias
- `PB`: stop bias
- `SB`: step bias

Bias unit: `V`

### Oscillator Level

- `OL`: oscillator level

Unit: `V`

### Reference Parameters

- `RA`: reference A
- `RB`: reference B

## DISPLAY C Output Codes

When `F1` is active, DISPLAY C is included in the output string.

Useful DISPLAY C unit codes from table `3-25`:

- `K`: kHz
- `V`: volts
- `A`: mA
- `R`: reference data

Examples:

- `K10` means `10 kHz`
- `V0.100` means `0.100 V`

## Display Function Codes

The 4192A uses separate function codes for DISPLAY A and DISPLAY B.

Common DISPLAY A choices:

- `A1`: `Z/Y`
- `A2`: `R/G`
- `A3`: `L`
- `A4`: `C`
- `A5`: `B-A (dB)`
- `A6`: `A (dBm/dBV)`
- `A7`: `B (dBm/dBV)`

Common DISPLAY B choices:

- `B1`: angle or related function depending on DISPLAY A mode
- `B2`: alternate paired function depending on DISPLAY A mode
- `B3`: third paired function depending on DISPLAY A mode

Important note:

DISPLAY B meaning depends on DISPLAY A mode. The manual gives the valid
pairings in table `3-23`. When adding more API coverage, use those pairings
directly instead of guessing combinations.

## Practical Rules For This Repo

These are the working rules for the HP 4192A implementation:

1. Keep `ping()` non-destructive.
2. Do not use `clear()` in `ping()`.
3. Separate recall codes from parameter-setting codes in both code and docs.
4. When a command meaning is unclear, stop and check the manual before
   implementing it.
5. Prefer small working slices of functionality over a large incomplete driver.

## Current Driver Scope

Right now the active driver only covers:

- `ping()`: connection information, current display functions, and spot
  frequency
- `configure(...)` keywords:
  - `frequency_hz`
  - `bias_voltage_v`
  - `osc_level_v`
  - `display_a`
  - `display_b`

That is intentional. More commands can be added once they are confirmed on the
real instrument.

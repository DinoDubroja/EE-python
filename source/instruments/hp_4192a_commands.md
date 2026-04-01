# HP 4192A Command Guide

This is the working command reference for the HP 4192A driver in this repo.

The goal of this document is practical:

- explain the HP 4192A remote-command style in plain language
- show which raw HP-IB codes the current Python API sends
- show which raw HP-IB codes `ping()` uses to read state back
- give examples you can use at the bench without reopening the full manual

The HP 4192A is not SCPI. It uses older HP-IB remote program codes.

## Manual Sections Used For The Current Driver

Whenever new driver coverage is added, these are the first manual sections to
check again:

- table `3-23`: control, mode, display, recall, trigger, and output-format codes
- table `3-24`: numeric parameter-setting codes
- paragraph `3-124`: format of numeric parameter-setting commands
- figure `3-36`: returned A/B/C data format
- table `3-25`: output codes for DISPLAY A, DISPLAY B, and DISPLAY C
- figure `3-38`: example spot-measurement program

## First Rule

Do not assume that every bus operation is harmless.

In this lab setup, VISA device clear reset the instrument frequency back to
`100 kHz`.

Because of that:

- `ping()` must not use `clear()`
- raw diagnostic scripts should avoid `clear()` unless that is the exact thing
  being tested
- when a readback path is uncertain, test it directly on the instrument before
  building it into the API

## Two Different Command Families

The manual separates commands into two groups. This distinction is important.

### 1. Control And Recall Codes

These come from table `3-23`.

Examples:

- `F1`: output `DISPLAY A/B/C`
- `F0`: output `DISPLAY A/B`
- `FRR`: recall spot frequency onto DISPLAY C for output
- `BIR`: recall spot bias onto DISPLAY C for output
- `OLR`: recall oscillator level onto DISPLAY C for output
- `C1`: circuit mode auto
- `C2`: circuit mode series
- `C3`: circuit mode parallel
- `T1`: trigger mode internal
- `T2`: trigger mode external
- `T3`: trigger mode hold/manual
- `EX`: execute / trigger

These are not numeric parameter-setting commands.

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

These commands carry a numeric value and end with `EN`.

## Numeric Parameter Format

Paragraph `3-124` describes the general parameter format as:

```text
XX+/-NNNN.NNNNEN
```

Practical meaning:

- `XX` is the parameter code, for example `FR`
- the number is the value
- `EN` terminates the parameter entry

Units depend on the parameter:

- frequency parameters use `kHz`
- spot bias uses `V`
- oscillator level uses `V`

## Current Python API

### `configure()` Keywords

The current high-level Python API supports these keywords:

- `frequency_hz`
- `bias_voltage_v`
- `osc_level_v`
- `bias_enabled`
- `trigger_mode`
- `measurement_mode`
- `zy_range`
- `circuit_mode`
- `display_a`
- `display_b`

### `get()`

The current driver also supports:

- `get(parameter_name)`

This is the single-parameter readback function for the 4192A in this repo.

Currently supported parameter names:

- `frequency_hz`
- `bias_voltage_v`
- `osc_level_v`
- `display_a`
- `display_b`
- `circuit_mode`

Not yet supported in `get()`:

- `bias_enabled`
- `trigger_mode`
- `measurement_mode`
- `zy_range`

These are intentionally omitted until the driver has a proven safe recall path
for them from the instrument.

Examples:

```python
frequency_hz = meter.get("frequency_hz")
bias_voltage_v = meter.get("bias_voltage_v")
display_a = meter.get("display_a")
```

Return style:

- numeric test parameters return numbers
- display parameters return high-level names such as `impedance`,
  `capacitance`, `phase_deg`, or `quality_factor`
- `circuit_mode` returns `series` or `parallel` only when the current display
  exposes that information

### `measure()`

The current driver also supports:

- `measure()`

This is the higher-level data-read function for the 4192A in this repo.
It returns only the current DISPLAY A and DISPLAY B numeric values.

Important:

- if DISPLAY A is `inductance` or `capacitance`, the Python API expects you to
  set `circuit_mode` explicitly as well
- if DISPLAY A is `impedance`, the driver uses series interpretation for the
  shared Z/Y family so the returned quantity is really impedance, not
  admittance
- if the instrument reports `overflow` or `uncalibrated`, `measure()` returns
  `math.nan` for that display value instead of stopping the program

### `configure()` Self-Check

The current driver does not treat `configure()` as "send and hope."

After it sends the requested command or commands, it reads the changed
parameter back from the instrument and prints one short confirmation line.

Uniform print format used by this repo:

- exact or accepted value:

  ```text
  HP 4192A LF Impedance Analyzer | frequency_hz -> 1 kHz
  ```

- instrument rounded the value to its own resolution:

  ```text
  HP 4192A LF Impedance Analyzer | osc_level_v requested 0.103 V -> instrument set 0.105 V
  ```

- readback is not available safely in the current state:

  ```text
  HP 4192A LF Impedance Analyzer | circuit_mode requested series -> readback unavailable
  ```

If the instrument readback disagrees with the requested change, the driver
raises a configuration-verification error instead of silently continuing.

### `ping()` Readback

The current `ping()` reads and reports:

- connection details derived from the VISA resource string
- current DISPLAY A function
- current DISPLAY B function
- circuit mode when it can be inferred from DISPLAY A
- spot frequency
- spot bias
- oscillator level

The current `ping()` does not report:

- `bias_enabled`
- `trigger_mode`
- `measurement_mode`
- `zy_range`

Those are not omitted by accident. The current driver simply does not have a
manual-backed safe recall path for them yet.

Everything shown by `ping()` is read from the instrument. It is not reported
from cached Python state.

### `measure()` Readback

`measure()` is intentionally different from `ping()`.

- `ping()` is for a readable instrument-state report
- `measure()` is for retrieving the current measurement data

`measure()` uses the current display setup and does not recall a new DISPLAY C
parameter before reading.

Basic path:

```text
F1
EX
READ
```

Meaning:

- `F1` requests DISPLAY A/B/C output
- `EX` triggers one output/measurement cycle
- the driver reads the returned A/B/C data string

Because `measure()` does not send `FRR`, `BIR`, or `OLR`, it does not
intentionally change which parameter DISPLAY C is following.

If DISPLAY A or DISPLAY B comes back with `O` (overflow) or `U`
(uncalibrated), `measure()` returns `math.nan` for that display value. This
keeps measurement loops running while still making it obvious that no actual
numeric reading is available for that point.

### `get()` Readback

`get()` is intentionally different from both `ping()` and `measure()`.

- `ping()` is for a readable full report
- `get()` is for one specific current parameter
- `measure()` is for current measurement data

Current readback paths:

- `get("frequency_hz")`

  ```text
  F1
  FRR
  EX
  READ
  ```

- `get("bias_voltage_v")`

  ```text
  F1
  BIR
  EX
  READ
  ```

- `get("osc_level_v")`

  ```text
  F1
  OLR
  EX
  READ
  ```

- `get("display_a")`, `get("display_b")`, and `get("circuit_mode")`
  use the function codes already present in the A/B output fields.

Important limitation:

- `get("circuit_mode")` is inferred from DISPLAY A codes such as `ZF`, `YF`,
  `LS`, `LP`, `CS`, and `CP`
- if the current display does not expose that information, `get("circuit_mode")`
  raises an error instead of guessing

## How `ping()` Reads The Instrument

The current driver uses this basic readback pattern:

```text
F1
<recall code>
EX
READ
```

Examples:

- frequency readback:

  ```text
  F1
  FRR
  EX
  READ
  ```

- spot-bias readback:

  ```text
  F1
  BIR
  EX
  READ
  ```

- oscillator-level readback:

  ```text
  F1
  OLR
  EX
  READ
  ```

Meaning:

- `F1` tells the instrument to return `DISPLAY A`, `DISPLAY B`, and `DISPLAY C`
- the recall code chooses what parameter appears on `DISPLAY C`
- `EX` triggers the output
- the driver reads one returned data string and parses it

Important practical note:

- because `ping()` recalls frequency, bias, and oscillator level one after
  another, DISPLAY C may end up showing the last recalled parameter after
  `ping()` finishes

## DISPLAY C Unit Codes

When `F1` is active, the returned data includes DISPLAY C.

Useful unit codes from table `3-25`:

- `K`: `kHz`
- `V`: volts
- `A`: mA
- `R`: reference data

Important note:

The manual OCR is inconsistent for the voltage unit code in some scanned text.
In bench use the driver accepts both `V` and `Y` for voltage readback so that
the parser stays robust while working from the scanned manual.

## Frequency

### High-Level Keyword

```python
meter.configure(frequency_hz=1_000)
```

### Raw Set Command

Spot frequency uses table `3-24` code `FR` with a value in `kHz`.

Examples:

- `FR1EN` -> `1 kHz`
- `FR10EN` -> `10 kHz`
- `FR100EN` -> `100 kHz`
- `FR0.005EN` -> `5 Hz`

Driver limits:

- valid Python range: `5 Hz` to `13 MHz`

### Raw Readback Command

Spot-frequency recall uses table `3-23` code:

- `FRR`

### `ping()` Readback Path

```text
F1
FRR
EX
READ
```

Expected DISPLAY C meaning:

- unit code `K`
- numeric value in `kHz`

### Driver Behavior After `configure(frequency_hz=...)`

After sending the set command, the driver also sends:

```text
FRR
```

The reason is simple: this gives the instrument a chance to make DISPLAY C
follow the last changed parameter.

Then the driver reads the frequency back and checks that the instrument really
accepted the new value.

## Spot Bias

### High-Level Keyword

```python
meter.configure(bias_voltage_v=0.5)
```

### Raw Set Command

Spot bias uses table `3-24` code `BI` with a value in volts.

Examples:

- `BI0.50EN` -> `+0.50 V`
- `BI-0.50EN` -> `-0.50 V`
- `BI10.00EN` -> `+10.00 V`

Driver limits:

- valid Python range: `-35.00 V` to `+35.00 V`
- driver rounds to the instrument resolution of `0.01 V`

### Raw Readback Command

Spot-bias recall uses table `3-23` code:

- `BIR`

### `ping()` Readback Path

```text
F1
BIR
EX
READ
```

Expected DISPLAY C meaning:

- voltage value in volts

### Driver Behavior After `configure(bias_voltage_v=...)`

After sending the set command, the driver also sends:

```text
BIR
```

This is the same DISPLAY-C-follow behavior used for spot frequency.

Then the driver reads the bias back and checks the actual instrument value.

## Oscillator Level

### High-Level Keyword

```python
meter.configure(osc_level_v=0.1)
```

### Raw Set Command

Oscillator level uses table `3-24` code `OL` with a value in volts.

Examples:

- `OL0.010EN` -> `10 mV`
- `OL0.100EN` -> `100 mV`
- `OL0.105EN` -> `105 mV`

Driver limits:

- valid Python range: `0.005 V` to `1.100 V`
- driver rounds to `0.001 V` from `0.005 V` to `0.100 V`
- driver rounds to `0.005 V` above `0.100 V` up to `1.100 V`

### Raw Readback Command

Oscillator-level recall uses table `3-23` code:

- `OLR`

### `ping()` Readback Path

```text
F1
OLR
EX
READ
```

Expected DISPLAY C meaning:

- voltage value in volts

### Driver Behavior After `configure(osc_level_v=...)`

After sending the set command, the driver also sends:

```text
OLR
```

This is the same DISPLAY-C-follow behavior used for the other numeric test
parameters.

Then the driver reads the oscillator level back and checks the actual
instrument value. If the requested value falls between supported instrument
steps, the driver prints both the requested and actual values instead of
treating that as an error.

## Bias Output Enable

### High-Level Keyword

```python
meter.configure(bias_enabled=True)
meter.configure(bias_enabled=False)
```

This is separate from `bias_voltage_v`.

Important:

- `bias_voltage_v=0` means the bias setpoint is `0 V`
- `bias_enabled=False` means the internal bias output is turned off
- these are not the same state on the real instrument

### Raw Control Codes

Bias ON/OFF uses table `3-23` codes:

- `I1` -> bias on
- `I0` -> bias off

The numeric bias setpoint still uses table `3-24`:

- `BI...EN` -> set spot bias value

### Practical Driver Behavior

Examples:

```python
meter.configure(bias_voltage_v=1.0, bias_enabled=True)
meter.configure(bias_voltage_v=1.0, bias_enabled=False)
```

The current driver sends the value-setting code first and the ON/OFF code
afterward. That makes it possible to keep a stored bias value while turning the
actual bias output off.

On the current bench setup, when bias output is off, the present readback path
reports the actual output as `0 V`.

### Readback Limitation

The current driver does not yet have a proven safe recall code for the bias
ON/OFF state itself.

Because of that:

- `get("bias_enabled")` is not implemented
- `ping()` does not report `bias_enabled`
- `configure()` prints `readback unavailable` for `bias_enabled`

Use `configure_test.py` to verify this on the front panel by checking the BIAS
ON indicator.

## Trigger Mode

### High-Level Keyword

```python
meter.configure(trigger_mode="hold")
```

Accepted values:

- `internal`
- `external`
- `hold`

### Raw Control Codes

Trigger mode uses table `3-23` codes:

- `T1` -> internal
- `T2` -> external
- `T3` -> hold/manual

The same table also says:

- `EX` is the execute / trigger code

### Important Practical Rule

The current readback path for `ping()`, `get()`, and `measure()` depends on
`EX`.

Because of that, the repo's manual `configure_test.py` intentionally skips
`ping()` immediately after the `trigger_mode="external"` step and restores a
safe trigger mode before continuing.

### Readback Limitation

The current driver does not yet have a proven safe recall path for trigger
mode.

Because of that:

- `get("trigger_mode")` is not implemented
- `ping()` does not report `trigger_mode`
- `configure()` prints `readback unavailable` for `trigger_mode`

## Measurement Mode

### High-Level Keyword

```python
meter.configure(measurement_mode="average")
```

Accepted values:

- `normal`
- `average`
- `high_speed`

The high-level API uses one keyword because the manual behavior is effectively
three mutually exclusive modes rather than two independent toggles.

### Raw Control Codes

From table `3-23`:

- `V0` -> average off
- `V1` -> average on
- `H0` -> high speed off
- `H1` -> high speed on

The driver combines them as:

- `normal` -> `V0`, `H0`
- `average` -> `V1`, `H0`
- `high_speed` -> `V0`, `H1`

### Readback Limitation

The current driver does not yet have a proven safe recall path for measurement
mode.

Because of that:

- `get("measurement_mode")` is not implemented
- `ping()` does not report `measurement_mode`
- `configure()` prints `readback unavailable` for `measurement_mode`

Use `configure_test.py` to verify this on the front panel by checking the
AVERAGE and HIGH SPEED indicators.

## ZY Range

### High-Level Keyword

```python
meter.configure(zy_range="10_kohm")
```

Accepted values:

- `auto`
- `1_ohm`
- `10_ohm`
- `100_ohm`
- `1_kohm`
- `10_kohm`
- `100_kohm`
- `1_mohm`

These names use the impedance side of the HP 4192A front-panel pairings.

### Raw Control Codes

From table `3-23`:

- `R1` -> 1 ohm / 10 S
- `R2` -> 10 ohm / 1 S
- `R3` -> 100 ohm / 100 mS
- `R4` -> 1 kohm / 10 mS
- `R5` -> 10 kohm / 1 mS
- `R6` -> 100 kohm / 100 uS
- `R7` -> 1 Mohm / 10 uS
- `R8` -> auto

### Readback Limitation

The current driver does not yet have a proven safe recall path for the current
ZY range mode.

Because of that:

- `get("zy_range")` is not implemented
- `ping()` does not report `zy_range`
- `configure()` prints `readback unavailable` for `zy_range`

Use `configure_test.py` to verify range changes directly on the front panel.

## Circuit Mode

### High-Level Keyword

```python
meter.configure(circuit_mode="series")
```

Accepted values:

- `auto`
- `series`
- `parallel`

### Raw Control Codes

Circuit mode uses table `3-23` codes:

- `C1` -> auto
- `C2` -> series
- `C3` -> parallel

### How `ping()` Reports Circuit Mode

The current driver does not use a separate circuit-mode recall code because the
manual tables used so far do not show one in the same style as `FRR`, `BIR`,
and `OLR`.

Instead, `ping()` infers circuit mode from the returned DISPLAY A function code:

- `ZF` -> impedance in series interpretation
- `YF` -> admittance in parallel interpretation
- `LS` -> inductance (series)
- `LP` -> inductance (parallel)
- `CS` -> capacitance (series)
- `CP` -> capacitance (parallel)

So:

- if DISPLAY A returns `ZF`, `ping()` reports `series`
- if DISPLAY A returns `YF`, `ping()` reports `parallel`
- if DISPLAY A returns `LS` or `CS`, `ping()` reports `series`
- if DISPLAY A returns `LP` or `CP`, `ping()` reports `parallel`

Important limitation:

When you set `circuit_mode="auto"`, the instrument may still report a concrete
series or parallel interpretation depending on what it chose for the current
measurement. `ping()` reports what DISPLAY A actually returns.

The same limitation affects `configure()` verification:

- if DISPLAY A readback contains enough information, `configure()` verifies the
  circuit mode
- if the current display family does not expose series/parallel information,
  `configure()` prints `readback unavailable`

## Display Functions

The current driver supports a small explicit set of display-function pairs. This
is intentional. It is better to support a few combinations correctly than to
guess a much larger matrix.

### Raw A/B Function Codes

From table `3-23`, the driver currently uses:

- `A1`: Z/Y family
- `A3`: L family
- `A4`: C family
- `B1`: first valid partner for the current DISPLAY A family
- `B2`: second valid partner for the current DISPLAY A family

### Supported High-Level Pairs

#### Impedance

- `display_a="impedance", display_b="phase_deg"` -> `A1`, `B1`
- `display_a="impedance", display_b="phase_rad"` -> `A1`, `B2`

Important:

- on the HP 4192A, the `A1` Z/Y family is shared
- the driver therefore uses `circuit_mode="series"` for `display_a="impedance"`
- if the instrument is left in parallel interpretation, the same `A1` family
  can read back as `YF` which means admittance rather than impedance

#### Inductance

- `display_a="inductance", display_b="quality_factor"` -> `A3`, `B1`
- `display_a="inductance", display_b="dissipation_factor"` -> `A3`, `B2`

#### Capacitance

- `display_a="capacitance", display_b="quality_factor"` -> `A4`, `B1`
- `display_a="capacitance", display_b="dissipation_factor"` -> `A4`, `B2`

Important:

- for `impedance`, the driver uses series interpretation in the shared Z/Y
  family so the readback stays in impedance rather than admittance
- for `inductance` and `capacitance`, also set `circuit_mode`
- that keeps the series/parallel interpretation explicit in the high-level API

### Example

```python
meter.configure(
    circuit_mode="series",
    display_a="inductance",
    display_b="quality_factor",
)
```

Raw commands sent:

```text
C2
A3
B1
```

### How `ping()` Reads Display Functions

`ping()` does not use a separate recall code for display functions.

Instead, it reads the function codes that are already present in the returned
DISPLAY A and DISPLAY B fields of the measurement output string.

For example, when the output contains:

- DISPLAY A function code `ZF`, the driver reports `impedance`
- DISPLAY B function code `TD`, the driver reports `phase (deg)`
- DISPLAY A function code `LS`, the driver reports `inductance (series)`
- DISPLAY B function code `QF`, the driver reports `quality factor`

## Bench Examples

### Read Spot Frequency

```text
F1
FRR
EX
READ
```

If DISPLAY C comes back as `K10`, the spot frequency is `10 kHz`.

### Read One Current Measurement Snapshot

Using the current display setup:

```text
F1
EX
READ
```

Python example:

```python
reading = meter.measure()

print(reading.display_a)
print(reading.display_b)
```

### Read Spot Bias

```text
F1
BIR
EX
READ
```

If DISPLAY C comes back as `V0.50`, the spot bias is `0.50 V`.

### Read Oscillator Level

```text
F1
OLR
EX
READ
```

If DISPLAY C comes back as `V0.100`, the oscillator level is `0.100 V`.

### Set Frequency Then Read It Back

```text
FR1EN
F1
FRR
EX
READ
```

Expected DISPLAY C:

```text
K1
```

### Set Bias Then Read It Back

```text
BI0.50EN
F1
BIR
EX
READ
```

Expected DISPLAY C:

```text
V0.50
```

### Set Oscillator Level Then Read It Back

```text
OL0.100EN
F1
OLR
EX
READ
```

Expected DISPLAY C:

```text
V0.100
```

## Practical Rules For This Repo

These are the working rules for the 4192A code:

1. Keep `ping()` non-destructive.
2. Never use VISA device clear in `ping()`.
3. Keep table `3-23` recall/control codes separate from table `3-24`
   numeric-setting codes in both code and documentation.
4. Only expose high-level keywords that have been checked against the manual.
5. Update this document every time new HP 4192A API coverage is added.

## Current Driver Scope

Right now the active driver covers:

- `ping()`
  - connection report
  - display A/B readback
  - inferred circuit mode
  - spot frequency
  - spot bias
  - oscillator level
- `get(parameter_name)`
  - `frequency_hz`
  - `bias_voltage_v`
  - `osc_level_v`
  - `display_a`
  - `display_b`
  - `circuit_mode`
- `configure(...)`
  - `frequency_hz`
  - `bias_voltage_v`
  - `osc_level_v`
  - `bias_enabled`
  - `trigger_mode`
  - `measurement_mode`
  - `zy_range`
  - `circuit_mode`
  - `display_a`
  - `display_b`
- `measure()`
  - current DISPLAY A value
  - current DISPLAY B value

More functionality should be added the same way:

- re-read the manual
- map high-level EE names to raw HP-IB codes
- verify behavior on the real instrument
- update this command guide at the same time

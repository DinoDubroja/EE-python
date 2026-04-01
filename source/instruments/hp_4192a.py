"""
HP 4192A LF Impedance Analyzer API.

Current scope:
- ping(): report connection details, current display functions, spot
  frequency, spot bias, and oscillator level
- get(): read one current parameter value from the instrument
- configure(): set spot frequency, spot bias, oscillator level, circuit mode,
  bias enable, trigger mode, measurement mode, range selection, and a small
  supported set of display-function pairs
- measure(): return one current A/B measurement pair
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import math
import re
import time
from typing import Callable, Literal, TypeAlias

from .instrument import (
    ConfigurationVerificationError,
    Instrument,
    InstrumentReport,
    format_configure_adjusted,
    format_configure_success,
    format_configure_unverified,
)
from .visa import VisaDevice


HP4192ADisplayA: TypeAlias = Literal[
    "impedance",
    "inductance",
    "capacitance",
]

HP4192ADisplayB: TypeAlias = Literal[
    "phase_deg",
    "phase_rad",
    "quality_factor",
    "dissipation_factor",
]

HP4192ACircuitMode: TypeAlias = Literal[
    "auto",
    "series",
    "parallel",
]

HP4192ATriggerMode: TypeAlias = Literal[
    "internal",
    "external",
    "hold",
]

HP4192AMeasurementMode: TypeAlias = Literal[
    "normal",
    "average",
    "high_speed",
]

HP4192AZYRange: TypeAlias = Literal[
    "auto",
    "1_ohm",
    "10_ohm",
    "100_ohm",
    "1_kohm",
    "10_kohm",
    "100_kohm",
    "1_mohm",
]

HP4192AGetParameter: TypeAlias = Literal[
    "frequency_hz",
    "bias_voltage_v",
    "osc_level_v",
    "display_a",
    "display_b",
    "circuit_mode",
]


_DISPLAY_PAIR_TO_CODES: dict[tuple[str, str], tuple[str, str]] = {
    ("impedance", "phase_deg"): ("A1", "B1"),
    ("impedance", "phase_rad"): ("A1", "B2"),
    ("inductance", "quality_factor"): ("A3", "B1"),
    ("inductance", "dissipation_factor"): ("A3", "B2"),
    ("capacitance", "quality_factor"): ("A4", "B1"),
    ("capacitance", "dissipation_factor"): ("A4", "B2"),
}

_DISPLAY_A_REQUEST_TO_CODES: dict[str, set[str]] = {
    "impedance": {"ZF"},
    "inductance": {"LS", "LP"},
    "capacitance": {"CS", "CP"},
}

_DISPLAY_B_REQUEST_TO_CODES: dict[str, set[str]] = {
    "phase_deg": {"TD"},
    "phase_rad": {"TR"},
    "quality_factor": {"QF"},
    "dissipation_factor": {"DF"},
}

_DISPLAY_A_CODE_TO_NAME: dict[str, str] = {
    "ZF": "impedance",
    "YF": "admittance",
    "RF": "resistance",
    "GF": "conductance",
    "LS": "inductance (series)",
    "LP": "inductance (parallel)",
    "CS": "capacitance (series)",
    "CP": "capacitance (parallel)",
    "BA": "gain difference",
    "AV": "display A in dBV",
    "BV": "display B in dBV",
    "AM": "display A in dBm",
    "BM": "display B in dBm",
}

_DISPLAY_A_CODE_TO_GET_VALUE: dict[str, str] = {
    "ZF": "impedance",
    "YF": "admittance",
    "RF": "resistance",
    "GF": "conductance",
    "LS": "inductance",
    "LP": "inductance",
    "CS": "capacitance",
    "CP": "capacitance",
    "BA": "gain_difference",
    "AV": "display_a_dbv",
    "BV": "display_b_dbv",
    "AM": "display_a_dbm",
    "BM": "display_b_dbm",
}

_DISPLAY_B_CODE_TO_NAME: dict[str, str] = {
    "TD": "phase (deg)",
    "TR": "phase (rad)",
    "XF": "reactance",
    "BF": "susceptance",
    "QF": "quality factor",
    "DF": "dissipation factor",
    "RF": "resistance",
    "GF": "conductance",
    "GD": "group delay",
    "UM": "unmeasure",
}

_DISPLAY_B_CODE_TO_GET_VALUE: dict[str, str] = {
    "TD": "phase_deg",
    "TR": "phase_rad",
    "XF": "reactance",
    "BF": "susceptance",
    "QF": "quality_factor",
    "DF": "dissipation_factor",
    "RF": "resistance",
    "GF": "conductance",
    "GD": "group_delay",
    "UM": "unmeasure",
}

_KNOWN_DISPLAY_A_FUNCTION_CODES = set(_DISPLAY_A_CODE_TO_NAME) | set(
    _DISPLAY_A_CODE_TO_GET_VALUE
)
_KNOWN_DISPLAY_B_FUNCTION_CODES = set(_DISPLAY_B_CODE_TO_NAME) | set(
    _DISPLAY_B_CODE_TO_GET_VALUE
)
_KNOWN_DEVIATION_MODE_CODES = {"N", "D", "P"}

_DISPLAY_A_CODE_TO_CIRCUIT_MODE: dict[str, str] = {
    "ZF": "series",
    "YF": "parallel",
    "LS": "series",
    "CS": "series",
    "LP": "parallel",
    "CP": "parallel",
}

_CIRCUIT_MODE_TO_CODE: dict[str, str] = {
    "auto": "C1",
    "series": "C2",
    "parallel": "C3",
}

_TRIGGER_MODE_TO_CODE: dict[str, str] = {
    "internal": "T1",
    "external": "T2",
    "hold": "T3",
}

_MEASUREMENT_MODE_TO_CODES: dict[str, tuple[str, ...]] = {
    "normal": ("V0", "H0"),
    "average": ("V1", "H0"),
    "high_speed": ("V0", "H1"),
}

_ZY_RANGE_TO_CODE: dict[str, str] = {
    "1_ohm": "R1",
    "10_ohm": "R2",
    "100_ohm": "R3",
    "1_kohm": "R4",
    "10_kohm": "R5",
    "100_kohm": "R6",
    "1_mohm": "R7",
    "auto": "R8",
}

_DISPLAY_C_VOLTAGE_UNIT_CODES = {"V", "Y"}

# The 4192A is noticeably happier when command/readback sequences are not sent
# at full PC speed. Keep these short so bench use stays responsive.
#
# Per-command delay after a plain write. This is intentionally left at zero
# because adding a gap after every command caused regressions. The more useful
# place to wait is after `EX` and after a full configure batch.
_HP4192A_COMMAND_DELAY_S = 0.0
#
# Delay after sending `EX` before reading the instrument response. This gives
# the 4192A time to complete the triggered output/update cycle.
_HP4192A_TRIGGER_SETTLE_S = 0.1
#
# Delay after a full configure batch before the driver starts verification
# readback. This is the main "let the instrument settle into the new state"
# pause, and it has the most impact on intermittent configure/self-test
# mismatches.
_HP4192A_POST_CONFIG_SETTLE_S = 0.1
#
# Delay before a retry when a numeric readback fails to parse or comes back in
# the wrong output state.
_HP4192A_READBACK_RETRY_DELAY_S = 0.1
#
# Number of attempts for numeric readbacks such as frequency, bias, and
# oscillator level.
_HP4192A_READBACK_ATTEMPTS = 5
#
# Delay before retrying a full configure-verification pass after a mismatch or
# a readback/state error.
_HP4192A_VERIFY_RETRY_DELAY_S = 0.1
#
# Number of full verification passes after `configure()` has sent its commands.
# This is broader than numeric readback retry: it also covers display-family
# and circuit-mode mismatches.
_HP4192A_VERIFY_ATTEMPTS = 5

_IMPLIED_CIRCUIT_MODE_FOR_DISPLAY_A: dict[str, str] = {
    "impedance": "series",
}


@dataclass(slots=True)
class _DisplayField:
    status_code: str
    function_code: str
    deviation_mode_code: str
    value_text: str


@dataclass(slots=True)
class _DisplayCField:
    unit_code: str
    value_text: str


@dataclass(slots=True)
class _OutputSnapshot:
    display_a: _DisplayField
    display_b: _DisplayField
    display_c: _DisplayCField
    raw: str


@dataclass(slots=True)
class HP4192AMeasurement:
    """
    One high-level HP 4192A measurement result.

    This is the return type of `HP4192A.measure()`.
    """

    display_a: float
    display_b: float


class HP4192A(Instrument):
    """
    HP 4192A driver for the active measurement-automation work.

    The implementation stays intentionally narrow. Only settings that were
    checked against the manual and selected for the current work are exposed.
    """

    def __init__(
        self,
        device: VisaDevice,
        *,
        trace_enabled: bool = False,
        trace_print_live: bool = False,
    ):
        super().__init__("HP 4192A LF Impedance Analyzer", device.resource_name)
        self._device = device
        self._trace_enabled = trace_enabled
        self._trace_print_live = trace_print_live
        self._trace_started_at = time.monotonic()
        self._trace_entries: list[str] = []

    @classmethod
    def open(
        cls,
        resource_name: str,
        *,
        timeout_ms: int = 5000,
        trace_enabled: bool = False,
        trace_print_live: bool = False,
    ) -> "HP4192A":
        """
        Open an HP 4192A through a VISA resource.

        Parameters
        ----------
        resource_name:
            VISA resource string, for example
            ``TCPIP0::192.168.1.244::gpib0,5::INSTR``.
        timeout_ms:
            VISA timeout in milliseconds.
        trace_enabled:
            When true, keep an in-memory trace of raw HP 4192A I/O for bench
            debugging.
        trace_print_live:
            When true together with `trace_enabled`, print trace entries live
            as they happen.
        """

        return cls(
            VisaDevice(resource_name, timeout_ms=timeout_ms),
            trace_enabled=trace_enabled,
            trace_print_live=trace_print_live,
        )

    def ping(self, *, show: bool = True) -> InstrumentReport:
        """
        Read the current HP 4192A state that is available through the current
        safe readback path.

        Current report content
        ----------------------
        - connection details derived from the VISA resource name
        - current DISPLAY A function
        - current DISPLAY B function
        - circuit mode when it can be inferred from DISPLAY A
        - spot frequency
        - spot bias
        - oscillator level
        - not trigger mode, measurement mode, bias enable, or ZY range, because
          those do not yet have a proven safe readback path in this driver
        
        Manual-backed readback path
        ---------------------------
        This method reads values from the instrument by using:

        - ``F1`` to include DISPLAY C in the output
        - a recall code from table 3-23 such as ``FRR``, ``BIR``, or ``OLR``
        - ``EX`` to trigger the output
        - one VISA read of the returned data string

        Important notes
        ---------------
        - This method does not send VISA device clear.
        - In this lab setup, VISA device clear reset the frequency to 100 kHz.
        - This method reports only parameters that currently have a proven
          manual-backed readback path in this driver.
        - Because the instrument is queried through recall codes such as
          `FRR`, `BIR`, and `OLR`, DISPLAY C may end up showing the last
          recalled parameter after `ping()` finishes.
        """

        state_rows: dict[str, object] = {}
        notes: list[str] = []

        try:
            frequency_snapshot = self._read_output_snapshot("FRR")
        except Exception as exc:
            notes.append(f"Could not read display functions and spot frequency: {exc}")
        else:
            display_a_name = _DISPLAY_A_CODE_TO_NAME.get(
                frequency_snapshot.display_a.function_code,
                f"unknown ({frequency_snapshot.display_a.function_code})",
            )
            display_b_name = _DISPLAY_B_CODE_TO_NAME.get(
                frequency_snapshot.display_b.function_code,
                f"unknown ({frequency_snapshot.display_b.function_code})",
            )

            state_rows["display A"] = display_a_name
            state_rows["display B"] = display_b_name

            circuit_mode = _DISPLAY_A_CODE_TO_CIRCUIT_MODE.get(
                frequency_snapshot.display_a.function_code
            )
            if circuit_mode is not None:
                state_rows["circuit mode"] = circuit_mode

            try:
                frequency_hz = _parse_spot_frequency_hz(frequency_snapshot)
            except Exception as exc:
                notes.append(f"Could not parse spot frequency from DISPLAY C: {exc}")
            else:
                state_rows["spot frequency"] = _format_frequency_hz(frequency_hz)

        try:
            bias_v = self._read_display_c_number(
                "BIR",
                expected_unit_codes=_DISPLAY_C_VOLTAGE_UNIT_CODES,
                parameter_name="spot bias",
            )
        except Exception as exc:
            notes.append(f"Could not read spot bias: {exc}")
        else:
            state_rows["spot bias"] = f"{_trim_zeros(bias_v)} V"

        try:
            osc_level_v = self._read_display_c_number(
                "OLR",
                expected_unit_codes=_DISPLAY_C_VOLTAGE_UNIT_CODES,
                parameter_name="oscillator level",
            )
        except Exception as exc:
            notes.append(f"Could not read oscillator level: {exc}")
        else:
            state_rows["oscillator level"] = f"{_trim_zeros(osc_level_v)} V"

        report = InstrumentReport(
            instrument_name=self.instrument_name,
            connection=self.connection_info,
            sections=[("State", state_rows)],
            notes=notes,
        )

        if show:
            print(report.to_text())

        return report

    def get(self, parameter_name: HP4192AGetParameter) -> float | str:
        """
        Read one current HP 4192A parameter value from the instrument.

        Supported parameter names
        -------------------------
        frequency_hz:
            Return the current spot frequency in hertz.

        bias_voltage_v:
            Return the current spot bias in volts.

        osc_level_v:
            Return the current oscillator level in volts.

        display_a:
            Return the current DISPLAY A measurement family as a high-level
            name such as `impedance`, `inductance`, or `capacitance`.

        display_b:
            Return the current DISPLAY B measurement family as a high-level
            name such as `phase_deg`, `quality_factor`, or
            `dissipation_factor`.

        circuit_mode:
            Return `series` or `parallel` when the current DISPLAY A function
            exposes that information.

        Not supported yet
        -----------------
        The current driver does not expose `get()` for these settings yet:

        - `bias_enabled`
        - `trigger_mode`
        - `measurement_mode`
        - `zy_range`

        Reason:
        The HP 4192A manual tables used by this driver do not provide a proven
        safe recall path for those states yet, and this repo avoids returning
        guessed or cached values as if they came from the instrument.

        Important limitation
        --------------------
        `circuit_mode` cannot always be read directly on the 4192A. The
        current driver infers it from DISPLAY A function codes such as `ZF`,
        `YF`, `LS`, `LP`, `CS`, and `CP`. If the current display does not
        expose that information, `get("circuit_mode")` raises an error instead
        of guessing.
        """

        if parameter_name == "frequency_hz":
            return self._read_spot_frequency_hz()

        if parameter_name == "bias_voltage_v":
            return self._read_display_c_number(
                "BIR",
                expected_unit_codes=_DISPLAY_C_VOLTAGE_UNIT_CODES,
                parameter_name="spot bias",
            )

        if parameter_name == "osc_level_v":
            return self._read_display_c_number(
                "OLR",
                expected_unit_codes=_DISPLAY_C_VOLTAGE_UNIT_CODES,
                parameter_name="oscillator level",
            )

        snapshot = self._read_output_snapshot("FRR")

        if parameter_name == "display_a":
            return _get_display_a_get_value(snapshot.display_a.function_code)

        if parameter_name == "display_b":
            return _get_display_b_get_value(snapshot.display_b.function_code)

        if parameter_name == "circuit_mode":
            circuit_mode = _DISPLAY_A_CODE_TO_CIRCUIT_MODE.get(
                snapshot.display_a.function_code
            )
            if circuit_mode is None:
                raise RuntimeError(
                    "current DISPLAY A function does not expose circuit_mode"
                )
            return circuit_mode

        raise ValueError(f"Unsupported get() parameter: {parameter_name!r}")

    def configure(
        self,
        *,
        # Test signal
        frequency_hz: float | None = None,
        bias_voltage_v: float | None = None,
        osc_level_v: float | None = None,
        # Bias output
        bias_enabled: bool | None = None,
        # Trigger and acquisition
        trigger_mode: HP4192ATriggerMode | None = None,
        measurement_mode: HP4192AMeasurementMode | None = None,
        # Range
        zy_range: HP4192AZYRange | None = None,
        # Measurement interpretation
        circuit_mode: HP4192ACircuitMode | None = None,
        # Measurement display
        display_a: HP4192ADisplayA | None = None,
        display_b: HP4192ADisplayB | None = None,
    ) -> None:
        """
        Change HP 4192A settings through one high-level entry point.

        Supported keywords
        ------------------
        frequency_hz:
            Spot frequency in hertz.
            Valid range: 5 Hz to 13 MHz.
            Sent as raw command ``FR...EN`` in kHz.

        bias_voltage_v:
            Spot DC bias in volts.
            Valid range: -35.00 V to +35.00 V.
            Instrument resolution: 0.01 V.
            Sent as raw command ``BI...EN``.

        osc_level_v:
            Oscillator level in volts.
            Valid range: 0.005 V to 1.100 V.
            Instrument resolution:
            - 0.001 V from 0.005 V to 0.100 V
            - 0.005 V above 0.100 V up to 1.100 V
            Sent as raw command ``OL...EN``.

        bias_enabled:
            Enable or disable the internal DC bias output.
            Accepted values:
            - ``True``
            - ``False``

            Sent as raw command ``I1`` or ``I0`` from table 3-23.

            Important:
            - this is separate from `bias_voltage_v`
            - `bias_voltage_v=0` does not mean bias output is off
            - when `bias_enabled=False`, the current readback path reports the
              actual output as `0 V` even if a nonzero bias value was requested
              in the same configure() call
            - the current driver does not yet have a proven safe readback path
              for the bias ON/OFF state, so configure() reports this keyword as
              `readback unavailable`

        trigger_mode:
            Measurement trigger source / behavior.
            Accepted values:
            - ``"internal"``
            - ``"external"``
            - ``"hold"``

            Sent as raw command ``T1``, ``T2``, or ``T3`` from table 3-23.

            The current driver does not yet have a proven safe readback path
            for trigger mode, so configure() reports this keyword as
            `readback unavailable`.

        measurement_mode:
            Speed / averaging behavior of the 4192A.
            Accepted values:
            - ``"normal"``
            - ``"average"``
            - ``"high_speed"``

            Sent using the table 3-23 mode codes:
            - ``normal`` -> ``V0`` and ``H0``
            - ``average`` -> ``V1`` and ``H0``
            - ``high_speed`` -> ``V0`` and ``H1``

            The current driver does not yet have a proven safe readback path
            for measurement mode, so configure() reports this keyword as
            `readback unavailable`.

        zy_range:
            Impedance/admittance range selection.
            Accepted values:
            - ``"auto"``
            - ``"1_ohm"``
            - ``"10_ohm"``
            - ``"100_ohm"``
            - ``"1_kohm"``
            - ``"10_kohm"``
            - ``"100_kohm"``
            - ``"1_mohm"``

            These correspond to the HP 4192A ZY RANGE keys:
            - ``1_ohm`` -> ``R1`` (1 ohm / 10 S)
            - ``10_ohm`` -> ``R2`` (10 ohm / 1 S)
            - ``100_ohm`` -> ``R3`` (100 ohm / 100 mS)
            - ``1_kohm`` -> ``R4`` (1 kohm / 10 mS)
            - ``10_kohm`` -> ``R5`` (10 kohm / 1 mS)
            - ``100_kohm`` -> ``R6`` (100 kohm / 100 uS)
            - ``1_mohm`` -> ``R7`` (1 Mohm / 10 uS)
            - ``auto`` -> ``R8``

            The current driver does not yet have a proven safe readback path
            for the selected ZY range state, so configure() reports this
            keyword as `readback unavailable`.

        circuit_mode:
            How the instrument interprets L and C displays.
            Accepted values:
            - ``"auto"``
            - ``"series"``
            - ``"parallel"``

            Sent as raw command ``C1``, ``C2``, or ``C3`` from table 3-23.
            `ping()` reports circuit mode only when it can be inferred from the
            current DISPLAY A readback, for example ``LS`` or ``CP``.

            HP 4192A note for the Z/Y family:
            - `display_a="impedance"` requires series interpretation
            - the driver therefore forces series mode for that display family
              when `circuit_mode` is omitted
            - if `display_a="impedance"` is combined with
              `circuit_mode="parallel"` or `circuit_mode="auto"`, the driver
              raises an error because that conflicts with the requested
              high-level quantity

        display_a, display_b:
            High-level measurement display selection.
            If either keyword is provided, both must be provided together.

            If `display_a` is `inductance` or `capacitance`, `circuit_mode`
            must also be provided explicitly. This keeps the API clear about
            whether you want series or parallel interpretation.

            If `display_a` is `impedance`, the driver uses series mode because
            that is how the HP 4192A exposes impedance rather than admittance
            in the shared Z/Y family.

            Currently supported pairs:
            - ``display_a="impedance"``, ``display_b="phase_deg"``
            - ``display_a="impedance"``, ``display_b="phase_rad"``
            - ``display_a="inductance"``, ``display_b="quality_factor"``
            - ``display_a="inductance"``, ``display_b="dissipation_factor"``
            - ``display_a="capacitance"``, ``display_b="quality_factor"``
            - ``display_a="capacitance"``, ``display_b="dissipation_factor"``

            These pairs are sent as A/B function codes from table 3-23.

        Examples
        --------
        Set only frequency:

        ``meter.configure(frequency_hz=1_000)``

        Set frequency, bias, and oscillator level:

        ``meter.configure(frequency_hz=1_000, bias_voltage_v=0.5, osc_level_v=0.1)``

        Turn bias output off while keeping a stored bias setpoint:

        ``meter.configure(bias_voltage_v=1.0, bias_enabled=False)``

        Select average mode:

        ``meter.configure(measurement_mode="average")``

        Select a manual impedance range:

        ``meter.configure(zy_range="10_kohm")``

        Set inductance mode in series with quality factor:

        ``meter.configure(circuit_mode="series", display_a="inductance", display_b="quality_factor")``

        Set a common impedance display pair:

        ``meter.configure(display_a="impedance", display_b="phase_deg")``

        DISPLAY C behavior
        ------------------
        If `frequency_hz`, `bias_voltage_v`, or `osc_level_v` is changed, the
        driver also sends the matching recall code (`FRR`, `BIR`, or `OLR`)
        after the set command. This gives the instrument a chance to make
        DISPLAY C follow the last changed numeric test parameter.

        Configure self-check
        --------------------
        After sending each requested setting, this method reads the instrument
        state back and prints one short confirmation line per changed
        parameter.

        To reduce false failures from occasional stale readback, the driver
        retries the full verification pass a small number of times before it
        gives up and raises.

        Behavior:
        - if the actual instrument value matches the requested value, a normal
          confirmation line is printed
        - if the instrument accepts the change but rounds it to its own
          resolution, the requested and actual values are both printed
        - if the readback disagrees with the requested change, this method
          raises `ConfigurationVerificationError`
        - if a parameter has no safe readback path in the current state, the
          method prints `readback unavailable` instead of guessing
        """

        commands: list[str] = []
        latest_display_c_recall_code: str | None = None
        expected_frequency_hz: float | None = None
        expected_bias_voltage_v: float | None = None
        expected_osc_level_v: float | None = None
        effective_circuit_mode = circuit_mode

        if frequency_hz is not None:
            frequency_hz = _validate_frequency_hz(frequency_hz)
            expected_frequency_hz = _normalize_frequency_hz(frequency_hz)
            commands.append(_format_spot_frequency_set_command(frequency_hz))
            latest_display_c_recall_code = "FRR"

        if bias_voltage_v is not None:
            bias_voltage_v = _validate_bias_voltage_v(bias_voltage_v)
            expected_bias_voltage_v = _normalize_bias_voltage_v(bias_voltage_v)
            commands.append(_format_spot_bias_set_command(bias_voltage_v))
            latest_display_c_recall_code = "BIR"

        if osc_level_v is not None:
            osc_level_v = _validate_osc_level_v(osc_level_v)
            expected_osc_level_v = _normalize_osc_level_v(osc_level_v)
            commands.append(_format_osc_level_set_command(osc_level_v))
            latest_display_c_recall_code = "OLR"

        if bias_enabled is not None:
            bias_enabled = _validate_bool_parameter("bias_enabled", bias_enabled)
            if bias_enabled is False and expected_bias_voltage_v is not None:
                expected_bias_voltage_v = 0.0

        if trigger_mode is not None:
            commands.append(_get_trigger_mode_code(trigger_mode))

        if measurement_mode is not None:
            commands.extend(_get_measurement_mode_codes(measurement_mode))

        if zy_range is not None:
            commands.append(_get_zy_range_code(zy_range))

        if display_a is not None or display_b is not None:
            if display_a is None or display_b is None:
                raise ValueError("display_a and display_b must be provided together")

            implied_circuit_mode = _IMPLIED_CIRCUIT_MODE_FOR_DISPLAY_A.get(display_a)
            if implied_circuit_mode is not None:
                if circuit_mode is None:
                    effective_circuit_mode = implied_circuit_mode
                elif circuit_mode != implied_circuit_mode:
                    raise ValueError(
                        f"display_a={display_a!r} requires circuit_mode={implied_circuit_mode!r}"
                    )

            if display_a in {"inductance", "capacitance"} and circuit_mode is None:
                raise ValueError(
                    "display_a='inductance' or display_a='capacitance' "
                    "require circuit_mode to be set explicitly"
                )

        if effective_circuit_mode is not None:
            commands.append(_get_circuit_mode_code(effective_circuit_mode))

        if display_a is not None and display_b is not None:
            commands.extend(_get_display_pair_codes(display_a, display_b))

        if bias_enabled is not None:
            commands.append(_get_bias_enabled_code(bias_enabled))

        requested_items = []
        for key, value in (
            ("frequency_hz", frequency_hz),
            ("bias_voltage_v", bias_voltage_v),
            ("osc_level_v", osc_level_v),
            ("bias_enabled", bias_enabled),
            ("trigger_mode", trigger_mode),
            ("measurement_mode", measurement_mode),
            ("zy_range", zy_range),
            ("circuit_mode", effective_circuit_mode),
            ("display_a", display_a),
            ("display_b", display_b),
        ):
            if value is not None:
                requested_items.append(f"{key}={value!r}")
        if requested_items:
            self._trace("CONFIG", ", ".join(requested_items))

        for command in commands:
            self._write_command(command)

        try:
            messages = self._verify_configuration_with_retry(
                frequency_hz=frequency_hz,
                expected_frequency_hz=expected_frequency_hz,
                bias_voltage_v=bias_voltage_v,
                expected_bias_voltage_v=expected_bias_voltage_v,
                osc_level_v=osc_level_v,
                expected_osc_level_v=expected_osc_level_v,
                bias_enabled=bias_enabled,
                trigger_mode=trigger_mode,
                measurement_mode=measurement_mode,
                zy_range=zy_range,
                effective_circuit_mode=effective_circuit_mode,
                display_a=display_a,
                display_b=display_b,
                commands_were_sent=bool(commands),
            )
            for message in messages:
                print(message)
        finally:
            if latest_display_c_recall_code is not None:
                self._write_command(latest_display_c_recall_code)

    def measure(self) -> HP4192AMeasurement:
        """
        Trigger one HP 4192A measurement and return the current DISPLAY A/B
        values.

        Return value
        ------------
        The returned `HP4192AMeasurement` contains only:

        - `display_a`: numeric value currently shown on DISPLAY A
        - `display_b`: numeric value currently shown on DISPLAY B

        Status handling
        ---------------
        If DISPLAY A or DISPLAY B reports `overflow` or `uncalibrated`,
        `measure()` returns `math.nan` for that display value instead of
        raising. This keeps point-by-point measurement loops running while
        still making invalid measurement values obvious in the returned data.

        Real communication or parsing failures still raise an error.

        Manual-backed measurement path
        ------------------------------
        This method uses the current display setup and sends:

        - ``F1`` to request DISPLAY A/B/C output
        - ``EX`` to execute one measurement/output cycle
        - one VISA read of the returned data string

        Important notes
        ---------------
        - `measure()` does not send a recall code such as `FRR` or `BIR`.
        - Because of that, it does not intentionally change which parameter is
          shown on DISPLAY C.
        - The returned numeric values depend on the current display setup, for
          example impedance/phase or inductance/Q.
        """

        snapshot = self._read_output_snapshot()

        return HP4192AMeasurement(
            display_a=_parse_numeric_measurement_field(
                snapshot.display_a,
                display_name="DISPLAY A",
            ),
            display_b=_parse_numeric_measurement_field(
                snapshot.display_b,
                display_name="DISPLAY B",
            ),
        )

    def _verify_configuration_with_retry(
        self,
        *,
        frequency_hz: float | None,
        expected_frequency_hz: float | None,
        bias_voltage_v: float | None,
        expected_bias_voltage_v: float | None,
        osc_level_v: float | None,
        expected_osc_level_v: float | None,
        bias_enabled: bool | None,
        trigger_mode: HP4192ATriggerMode | None,
        measurement_mode: HP4192AMeasurementMode | None,
        zy_range: HP4192AZYRange | None,
        effective_circuit_mode: HP4192ACircuitMode | None,
        display_a: HP4192ADisplayA | None,
        display_b: HP4192ADisplayB | None,
        commands_were_sent: bool,
    ) -> list[str]:
        if commands_were_sent:
            time.sleep(_HP4192A_POST_CONFIG_SETTLE_S)

        last_exception: Exception | None = None
        last_category = "unknown"

        for attempt_index in range(_HP4192A_VERIFY_ATTEMPTS):
            attempt_number = attempt_index + 1
            self._trace(
                "VERIFY",
                f"attempt {attempt_number}/{_HP4192A_VERIFY_ATTEMPTS}",
            )

            try:
                return self._verify_configuration_once(
                    frequency_hz=frequency_hz,
                    expected_frequency_hz=expected_frequency_hz,
                    bias_voltage_v=bias_voltage_v,
                    expected_bias_voltage_v=expected_bias_voltage_v,
                    osc_level_v=osc_level_v,
                    expected_osc_level_v=expected_osc_level_v,
                    bias_enabled=bias_enabled,
                    trigger_mode=trigger_mode,
                    measurement_mode=measurement_mode,
                    zy_range=zy_range,
                    effective_circuit_mode=effective_circuit_mode,
                    display_a=display_a,
                    display_b=display_b,
                )
            except Exception as exc:
                last_exception = exc
                last_category = _classify_hp4192a_exception(exc)
                self._trace(
                    "VERIFY",
                    f"attempt {attempt_number} failed ({last_category}): {exc}",
                )

                if attempt_number >= _HP4192A_VERIFY_ATTEMPTS:
                    break

                time.sleep(_HP4192A_VERIFY_RETRY_DELAY_S)

        if isinstance(last_exception, ConfigurationVerificationError):
            raise ConfigurationVerificationError(
                "configure verification failed after "
                f"{_HP4192A_VERIFY_ATTEMPTS} attempts "
                f"({last_category}): {last_exception}"
            ) from last_exception

        raise RuntimeError(
            "configure verification failed after "
            f"{_HP4192A_VERIFY_ATTEMPTS} attempts "
            f"({last_category}): {last_exception}"
        ) from last_exception

    def _verify_configuration_once(
        self,
        *,
        frequency_hz: float | None,
        expected_frequency_hz: float | None,
        bias_voltage_v: float | None,
        expected_bias_voltage_v: float | None,
        osc_level_v: float | None,
        expected_osc_level_v: float | None,
        bias_enabled: bool | None,
        trigger_mode: HP4192ATriggerMode | None,
        measurement_mode: HP4192AMeasurementMode | None,
        zy_range: HP4192AZYRange | None,
        effective_circuit_mode: HP4192ACircuitMode | None,
        display_a: HP4192ADisplayA | None,
        display_b: HP4192ADisplayB | None,
    ) -> list[str]:
        messages: list[str] = []
        snapshot_for_display_checks: _OutputSnapshot | None = None

        if any(
            value is not None
            for value in (frequency_hz, effective_circuit_mode, display_a, display_b)
        ):
            snapshot_for_display_checks = self._read_output_snapshot("FRR")

        if frequency_hz is not None:
            if snapshot_for_display_checks is None:
                raise ConfigurationVerificationError(
                    "frequency_hz was changed but no frequency readback was captured"
                )

            actual_frequency_hz = _parse_spot_frequency_hz(snapshot_for_display_checks)
            messages.append(
                _verify_numeric_setting(
                    instrument_name=self.instrument_name,
                    parameter_name="frequency_hz",
                    requested_value=frequency_hz,
                    expected_value=expected_frequency_hz,
                    actual_value=actual_frequency_hz,
                    requested_text=_format_frequency_hz(frequency_hz),
                    actual_text=_format_frequency_hz(actual_frequency_hz),
                    absolute_tolerance=1e-6,
                )
            )

        if bias_voltage_v is not None:
            actual_bias_voltage_v = self._read_display_c_number(
                "BIR",
                expected_unit_codes=_DISPLAY_C_VOLTAGE_UNIT_CODES,
                parameter_name="spot bias",
            )
            messages.append(
                _verify_numeric_setting(
                    instrument_name=self.instrument_name,
                    parameter_name="bias_voltage_v",
                    requested_value=bias_voltage_v,
                    expected_value=expected_bias_voltage_v,
                    actual_value=actual_bias_voltage_v,
                    requested_text=f"{_trim_zeros(bias_voltage_v)} V",
                    actual_text=f"{_trim_zeros(actual_bias_voltage_v)} V",
                    absolute_tolerance=1e-9,
                )
            )

        if osc_level_v is not None:
            actual_osc_level_v = self._read_display_c_number(
                "OLR",
                expected_unit_codes=_DISPLAY_C_VOLTAGE_UNIT_CODES,
                parameter_name="oscillator level",
            )
            messages.append(
                _verify_numeric_setting(
                    instrument_name=self.instrument_name,
                    parameter_name="osc_level_v",
                    requested_value=osc_level_v,
                    expected_value=expected_osc_level_v,
                    actual_value=actual_osc_level_v,
                    requested_text=f"{_trim_zeros(osc_level_v)} V",
                    actual_text=f"{_trim_zeros(actual_osc_level_v)} V",
                    absolute_tolerance=1e-9,
                )
            )

        if display_a is not None and display_b is not None:
            if snapshot_for_display_checks is None:
                raise ConfigurationVerificationError(
                    "display_a/display_b were changed but no display readback was captured"
                )

            actual_display_a_name = _DISPLAY_A_CODE_TO_NAME.get(
                snapshot_for_display_checks.display_a.function_code,
                f"unknown ({snapshot_for_display_checks.display_a.function_code})",
            )
            actual_display_b_name = _DISPLAY_B_CODE_TO_NAME.get(
                snapshot_for_display_checks.display_b.function_code,
                f"unknown ({snapshot_for_display_checks.display_b.function_code})",
            )

            messages.append(
                _verify_display_setting(
                    instrument_name=self.instrument_name,
                    parameter_name="display_a",
                    requested_value=display_a,
                    actual_code=snapshot_for_display_checks.display_a.function_code,
                    allowed_codes=_DISPLAY_A_REQUEST_TO_CODES[display_a],
                    actual_text=actual_display_a_name,
                )
            )
            messages.append(
                _verify_display_setting(
                    instrument_name=self.instrument_name,
                    parameter_name="display_b",
                    requested_value=display_b,
                    actual_code=snapshot_for_display_checks.display_b.function_code,
                    allowed_codes=_DISPLAY_B_REQUEST_TO_CODES[display_b],
                    actual_text=actual_display_b_name,
                )
            )

        if effective_circuit_mode is not None:
            if snapshot_for_display_checks is None:
                raise ConfigurationVerificationError(
                    "circuit_mode was changed but no display readback was captured"
                )

            actual_circuit_mode = _DISPLAY_A_CODE_TO_CIRCUIT_MODE.get(
                snapshot_for_display_checks.display_a.function_code
            )
            if actual_circuit_mode is None:
                messages.append(
                    format_configure_unverified(
                        self.instrument_name,
                        "circuit_mode",
                        effective_circuit_mode,
                    )
                )
            elif effective_circuit_mode == "auto":
                messages.append(
                    format_configure_adjusted(
                        self.instrument_name,
                        "circuit_mode",
                        "auto",
                        actual_circuit_mode,
                    )
                )
            elif actual_circuit_mode != effective_circuit_mode:
                raise ConfigurationVerificationError(
                    "circuit_mode verification failed: "
                    f"requested {effective_circuit_mode!r}, instrument reports {actual_circuit_mode!r}"
                )
            else:
                messages.append(
                    format_configure_success(
                        self.instrument_name,
                        "circuit_mode",
                        actual_circuit_mode,
                    )
                )

        if bias_enabled is not None:
            messages.append(
                format_configure_unverified(
                    self.instrument_name,
                    "bias_enabled",
                    str(bias_enabled),
                )
            )

        if trigger_mode is not None:
            messages.append(
                format_configure_unverified(
                    self.instrument_name,
                    "trigger_mode",
                    trigger_mode,
                )
            )

        if measurement_mode is not None:
            messages.append(
                format_configure_unverified(
                    self.instrument_name,
                    "measurement_mode",
                    measurement_mode,
                )
            )

        if zy_range is not None:
            messages.append(
                format_configure_unverified(
                    self.instrument_name,
                    "zy_range",
                    zy_range,
                )
            )

        return messages

    def close(self) -> None:
        """
        Close the VISA connection to the instrument.
        """

        self._device.close()

    def set_trace(
        self,
        *,
        enabled: bool = True,
        print_live: bool = False,
    ) -> None:
        """
        Enable or disable raw HP 4192A I/O tracing.
        """

        self._trace_enabled = enabled
        self._trace_print_live = print_live if enabled else False

    def clear_trace_log(self) -> None:
        """
        Clear the accumulated in-memory trace log.
        """

        self._trace_entries.clear()
        self._trace_started_at = time.monotonic()

    def get_trace_log(self) -> list[str]:
        """
        Return the current in-memory trace log.
        """

        return list(self._trace_entries)

    def format_trace_log(self) -> str:
        """
        Return the current in-memory trace log as plain text.
        """

        if not self._trace_entries:
            return "(trace log is empty)"
        return "\n".join(self._trace_entries)

    def _read_spot_frequency_hz(self) -> float:
        return self._retry_readback(
            lambda: _parse_spot_frequency_hz(self._read_output_snapshot("FRR")),
            parameter_name="spot frequency",
        )

    def _trace(self, category: str, message: str) -> None:
        if not self._trace_enabled:
            return

        elapsed_s = time.monotonic() - self._trace_started_at
        entry = f"[{elapsed_s:8.3f} s] {category:<8} {message}"
        self._trace_entries.append(entry)

        if self._trace_print_live:
            print(entry)

    def _retry_readback(self, reader: Callable[[], float], *, parameter_name: str) -> float:
        last_exception: Exception | None = None

        for attempt_index in range(_HP4192A_READBACK_ATTEMPTS):
            attempt_number = attempt_index + 1
            self._trace(
                "READTRY",
                f"{parameter_name}: attempt {attempt_number}/{_HP4192A_READBACK_ATTEMPTS}",
            )
            try:
                return reader()
            except Exception as exc:
                last_exception = exc
                self._trace(
                    "READTRY",
                    f"{parameter_name}: attempt {attempt_number} failed ({_classify_hp4192a_exception(exc)}): {exc}",
                )
                if attempt_number >= _HP4192A_READBACK_ATTEMPTS:
                    break
                time.sleep(_HP4192A_READBACK_RETRY_DELAY_S)

        raise RuntimeError(
            f"{parameter_name} readback failed after {_HP4192A_READBACK_ATTEMPTS} attempts: "
            f"{last_exception}"
        ) from last_exception

    def _read_display_c_number(
        self,
        recall_code: str,
        *,
        expected_unit_codes: set[str],
        parameter_name: str,
    ) -> float:
        return self._retry_readback(
            lambda: _parse_display_c_number(
                self._read_output_snapshot(recall_code).display_c,
                expected_unit_codes=expected_unit_codes,
                parameter_name=parameter_name,
            ),
            parameter_name=parameter_name,
        )

    def _read_output_snapshot(self, recall_code: str | None = None) -> _OutputSnapshot:
        """
        Read one DISPLAY A/B/C output snapshot.

        Manual basis:
        - Table 3-23: ``F1`` selects DISPLAY A/B/C output.
        - Table 3-23: optional recall codes such as ``FRR``, ``BIR``, and
          ``OLR`` choose which parameter is shown on DISPLAY C.
        - Table 3-23: ``EX`` triggers the output.
        - Figure 3-36 and table 3-25 define the returned data format.

        Important:
        - Do not send VISA device clear here. On the real instrument in this lab
          setup, device clear reset the frequency to 100 kHz.
        """

        self._trace("SNAPSHOT", f"start recall={recall_code or '-'}")
        self._write_command("F1")
        if recall_code is not None:
            self._write_command(recall_code)
        self._write_command("EX", settle_s=_HP4192A_TRIGGER_SETTLE_S)

        raw = self._device.read().strip()
        self._trace("READ", raw or "<empty>")
        if not raw:
            raise RuntimeError("instrument returned no data")

        return _parse_output_snapshot(raw)

    def _write_command(self, command: str, *, settle_s: float = _HP4192A_COMMAND_DELAY_S) -> None:
        self._trace("WRITE", command)
        self._device.write(command)
        if settle_s > 0.0:
            self._trace("SLEEP", f"{settle_s:.3f} s after {command}")
            time.sleep(settle_s)


def _validate_frequency_hz(value: float) -> float:
    numeric_value = _require_real_number("frequency_hz", value)
    if not 5.0 <= numeric_value <= 13_000_000.0:
        raise ValueError("frequency_hz must be between 5 Hz and 13 MHz")
    return numeric_value


def _validate_bias_voltage_v(value: float) -> float:
    numeric_value = _require_real_number("bias_voltage_v", value)
    if not -35.0 <= numeric_value <= 35.0:
        raise ValueError("bias_voltage_v must be between -35.00 V and +35.00 V")
    return numeric_value


def _validate_osc_level_v(value: float) -> float:
    numeric_value = _require_real_number("osc_level_v", value)
    if not 0.005 <= numeric_value <= 1.100:
        raise ValueError("osc_level_v must be between 0.005 V and 1.100 V")
    return numeric_value


def _validate_bool_parameter(parameter_name: str, value: bool) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{parameter_name} must be bool")
    return value


def _require_real_number(parameter_name: str, value: float) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{parameter_name} must be a real number, not bool")

    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{parameter_name} must be a real number") from exc

    if not math.isfinite(numeric_value):
        raise ValueError(f"{parameter_name} must be finite")

    return numeric_value


def _get_display_pair_codes(display_a: str, display_b: str) -> tuple[str, str]:
    pair = (display_a, display_b)
    try:
        return _DISPLAY_PAIR_TO_CODES[pair]
    except KeyError as exc:
        supported_pairs = ", ".join(
            f"({a}, {b})" for a, b in sorted(_DISPLAY_PAIR_TO_CODES)
        )
        raise ValueError(
            f"Unsupported display pair {pair}. Supported pairs: {supported_pairs}"
        ) from exc


def _get_circuit_mode_code(circuit_mode: str) -> str:
    try:
        return _CIRCUIT_MODE_TO_CODE[circuit_mode]
    except KeyError as exc:
        supported_modes = ", ".join(sorted(_CIRCUIT_MODE_TO_CODE))
        raise ValueError(
            f"Unsupported circuit_mode {circuit_mode!r}. "
            f"Supported values: {supported_modes}"
        ) from exc


def _get_bias_enabled_code(bias_enabled: bool) -> str:
    return "I1" if bias_enabled else "I0"


def _get_trigger_mode_code(trigger_mode: str) -> str:
    try:
        return _TRIGGER_MODE_TO_CODE[trigger_mode]
    except KeyError as exc:
        supported_modes = ", ".join(sorted(_TRIGGER_MODE_TO_CODE))
        raise ValueError(
            f"Unsupported trigger_mode {trigger_mode!r}. "
            f"Supported values: {supported_modes}"
        ) from exc


def _get_measurement_mode_codes(measurement_mode: str) -> tuple[str, ...]:
    try:
        return _MEASUREMENT_MODE_TO_CODES[measurement_mode]
    except KeyError as exc:
        supported_modes = ", ".join(sorted(_MEASUREMENT_MODE_TO_CODES))
        raise ValueError(
            f"Unsupported measurement_mode {measurement_mode!r}. "
            f"Supported values: {supported_modes}"
        ) from exc


def _get_zy_range_code(zy_range: str) -> str:
    try:
        return _ZY_RANGE_TO_CODE[zy_range]
    except KeyError as exc:
        supported_ranges = ", ".join(sorted(_ZY_RANGE_TO_CODE))
        raise ValueError(
            f"Unsupported zy_range {zy_range!r}. "
            f"Supported values: {supported_ranges}"
        ) from exc


def _parse_output_snapshot(raw: str) -> _OutputSnapshot:
    fields = [field.strip() for field in re.split(r"[\r\n,]+", raw) if field.strip()]
    if len(fields) < 3:
        raise RuntimeError(f"unexpected output: {raw!r}")

    display_a = _parse_display_field(fields[0], display_name="DISPLAY A")
    display_b = _parse_display_field(fields[1], display_name="DISPLAY B")
    display_c = _parse_display_c_field(fields[2])

    return _OutputSnapshot(
        display_a=display_a,
        display_b=display_b,
        display_c=display_c,
        raw=raw,
    )


def _get_display_a_get_value(function_code: str) -> str:
    try:
        return _DISPLAY_A_CODE_TO_GET_VALUE[function_code]
    except KeyError as exc:
        raise RuntimeError(
            f"DISPLAY A function code {function_code!r} is not mapped for get()"
        ) from exc


def _get_display_b_get_value(function_code: str) -> str:
    try:
        return _DISPLAY_B_CODE_TO_GET_VALUE[function_code]
    except KeyError as exc:
        raise RuntimeError(
            f"DISPLAY B function code {function_code!r} is not mapped for get()"
        ) from exc


def _parse_display_field(field: str, *, display_name: str) -> _DisplayField:
    if len(field) < 5:
        raise RuntimeError(f"{display_name} field was too short: {field!r}")

    if display_name == "DISPLAY A":
        known_function_codes = _KNOWN_DISPLAY_A_FUNCTION_CODES
    else:
        known_function_codes = _KNOWN_DISPLAY_B_FUNCTION_CODES

    standard_function_code = field[1:3]
    standard_deviation_mode = field[3]
    if (
        standard_function_code not in known_function_codes
        and len(field) >= 6
        and field[1] == field[0]
        and field[2:4] in known_function_codes
        and field[4] in _KNOWN_DEVIATION_MODE_CODES
    ):
        return _DisplayField(
            status_code=field[0],
            function_code=field[2:4],
            deviation_mode_code=field[4],
            value_text=field[5:],
        )

    return _DisplayField(
        status_code=field[0],
        function_code=standard_function_code,
        deviation_mode_code=standard_deviation_mode,
        value_text=field[4:],
    )


def _parse_display_c_field(field: str) -> _DisplayCField:
    if len(field) < 2:
        raise RuntimeError(f"DISPLAY C field was too short: {field!r}")

    return _DisplayCField(
        unit_code=field[0],
        value_text=field[1:],
    )


def _parse_display_c_number(
    field: _DisplayCField,
    *,
    expected_unit_codes: set[str],
    parameter_name: str,
) -> float:
    if field.unit_code not in expected_unit_codes:
        allowed = ", ".join(sorted(expected_unit_codes))
        raise RuntimeError(
            f"{parameter_name} expected DISPLAY C unit code in {{{allowed}}}, "
            f"got {field.unit_code!r}"
        )

    try:
        return float(field.value_text)
    except ValueError as exc:
        raise RuntimeError(
            f"{parameter_name} value could not be parsed from DISPLAY C: {field.value_text!r}"
        ) from exc


def _parse_spot_frequency_hz(snapshot: _OutputSnapshot) -> float:
    return _parse_display_c_number(
        snapshot.display_c,
        expected_unit_codes={"K"},
        parameter_name="spot frequency",
    ) * 1000.0


def _normalize_frequency_hz(value: float) -> float:
    frequency_khz = value / 1000.0
    return float(_format_frequency_value_khz(frequency_khz)) * 1000.0


def _normalize_bias_voltage_v(value: float) -> float:
    return float(_format_decimal_with_step(value, step="0.01", places="0.01"))


def _normalize_osc_level_v(value: float) -> float:
    if value <= 0.100:
        return float(_format_decimal_with_step(value, step="0.001", places="0.001"))
    return float(_format_decimal_with_step(value, step="0.005", places="0.001"))


def _classify_hp4192a_exception(exc: Exception) -> str:
    if isinstance(exc, ConfigurationVerificationError):
        return "state mismatch"

    message = str(exc)
    communication_markers = (
        "returned no data",
        "expected DISPLAY C unit code",
        "could not be parsed",
        "too short",
        "unexpected output",
        "readback failed after",
    )
    if any(marker in message for marker in communication_markers):
        return "communication/readback"

    return "other"


def _verify_numeric_setting(
    *,
    instrument_name: str,
    parameter_name: str,
    requested_value: float,
    expected_value: float | None,
    actual_value: float,
    requested_text: str,
    actual_text: str,
    absolute_tolerance: float,
) -> str:
    if expected_value is None:
        raise ConfigurationVerificationError(
            f"{parameter_name} verification was requested without an expected value"
        )

    if not math.isclose(actual_value, expected_value, rel_tol=0.0, abs_tol=absolute_tolerance):
        raise ConfigurationVerificationError(
            f"{parameter_name} verification failed: "
            f"requested {requested_text}, instrument reports {actual_text}"
        )

    if math.isclose(actual_value, requested_value, rel_tol=0.0, abs_tol=absolute_tolerance):
        return format_configure_success(instrument_name, parameter_name, actual_text)

    return format_configure_adjusted(
        instrument_name,
        parameter_name,
        requested_text,
        actual_text,
    )


def _verify_display_setting(
    *,
    instrument_name: str,
    parameter_name: str,
    requested_value: str,
    actual_code: str,
    allowed_codes: set[str],
    actual_text: str,
) -> str:
    if actual_code not in allowed_codes:
        allowed_text = ", ".join(sorted(allowed_codes))
        raise ConfigurationVerificationError(
            f"{parameter_name} verification failed: "
            f"requested {requested_value!r}, instrument returned code {actual_code!r} "
            f"(expected one of {allowed_text})"
        )

    return format_configure_success(instrument_name, parameter_name, actual_text)


def _try_parse_float(value_text: str) -> float | None:
    try:
        return float(value_text)
    except ValueError:
        return None


def _parse_numeric_measurement_field(field: _DisplayField, *, display_name: str) -> float:
    if field.status_code == "O":
        return math.nan
    if field.status_code == "U":
        return math.nan
    if field.status_code != "N":
        raise RuntimeError(
            f"{display_name} measurement returned unknown status code {field.status_code!r}"
        )

    value = _try_parse_float(field.value_text)
    if value is None:
        raise RuntimeError(
            f"{display_name} measurement could not be parsed from {field.value_text!r}"
        )

    return value


def _format_spot_frequency_set_command(frequency_hz: float) -> str:
    """
    Build the HP 4192A SPOT FREQ set command.

    Manual basis:
    - Table 3-24: SPOT FREQ uses program code ``FR``.
    - Paragraph 3-124: the parameter terminator is ``EN``.
    - Units are kHz.
    """

    frequency_khz = frequency_hz / 1000.0
    value_text = _format_frequency_value_khz(frequency_khz)
    return f"FR{value_text}EN"


def _format_spot_bias_set_command(bias_voltage_v: float) -> str:
    """
    Build the HP 4192A SPOT BIAS set command.

    Manual basis:
    - Table 3-24: SPOT BIAS uses program code ``BI``.
    - Paragraph 3-124: units are volts and the parameter terminator is ``EN``.
    - Table 3-24: resolution is 0.01 V.
    """

    rounded_text = _format_decimal_with_step(bias_voltage_v, step="0.01", places="0.01")
    return f"BI{rounded_text}EN"


def _format_osc_level_set_command(osc_level_v: float) -> str:
    """
    Build the HP 4192A OSC LEVEL set command.

    Manual basis:
    - Table 3-24: OSC LEVEL uses program code ``OL``.
    - Paragraph 3-124: units are volts and the parameter terminator is ``EN``.
    - Table 3-24: resolution is 0.001 V up to 0.100 V, then 0.005 V.
    """

    if osc_level_v <= 0.100:
        rounded_text = _format_decimal_with_step(osc_level_v, step="0.001", places="0.001")
    else:
        rounded_text = _format_decimal_with_step(osc_level_v, step="0.005", places="0.001")

    return f"OL{rounded_text}EN"


def _format_decimal_with_step(value: float, *, step: str, places: str) -> str:
    value_decimal = Decimal(str(value))
    step_decimal = Decimal(step)
    quantized = (value_decimal / step_decimal).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    ) * step_decimal
    return format(quantized.quantize(Decimal(places)), "f")


def _format_frequency_value_khz(frequency_khz: float) -> str:
    rounded = round(frequency_khz, 6)
    return f"{rounded:.6f}".rstrip("0").rstrip(".")


def _format_frequency_hz(frequency_hz: float) -> str:
    if frequency_hz >= 1_000_000:
        return f"{_trim_zeros(frequency_hz / 1_000_000)} MHz"
    if frequency_hz >= 1_000:
        return f"{_trim_zeros(frequency_hz / 1_000)} kHz"
    return f"{_trim_zeros(frequency_hz)} Hz"


def _trim_zeros(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")

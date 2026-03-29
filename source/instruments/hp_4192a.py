"""
HP 4192A LF Impedance Analyzer API.

Current scope:
- ping(): report connection details, current display functions, spot
  frequency, spot bias, and oscillator level
- configure(): set spot frequency, spot bias, oscillator level, circuit mode,
  and a small supported set of display-function pairs
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import math
import re
from typing import Literal, TypeAlias

from .instrument import Instrument, InstrumentReport
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


_DISPLAY_PAIR_TO_CODES: dict[tuple[str, str], tuple[str, str]] = {
    ("impedance", "phase_deg"): ("A1", "B1"),
    ("impedance", "phase_rad"): ("A1", "B2"),
    ("inductance", "quality_factor"): ("A3", "B1"),
    ("inductance", "dissipation_factor"): ("A3", "B2"),
    ("capacitance", "quality_factor"): ("A4", "B1"),
    ("capacitance", "dissipation_factor"): ("A4", "B2"),
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

_DISPLAY_A_CODE_TO_CIRCUIT_MODE: dict[str, str] = {
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

_DISPLAY_C_VOLTAGE_UNIT_CODES = {"V", "Y"}


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


class HP4192A(Instrument):
    """
    HP 4192A driver for the active measurement-automation work.

    The implementation stays intentionally narrow. Only settings that were
    checked against the manual and selected for the current work are exposed.
    """

    def __init__(self, device: VisaDevice):
        super().__init__("HP 4192A LF Impedance Analyzer", device.resource_name)
        self._device = device

    @classmethod
    def open(cls, resource_name: str, *, timeout_ms: int = 5000) -> "HP4192A":
        """
        Open an HP 4192A through a VISA resource.

        Parameters
        ----------
        resource_name:
            VISA resource string, for example
            ``TCPIP0::192.168.1.244::gpib0,5::INSTR``.
        timeout_ms:
            VISA timeout in milliseconds.
        """

        return cls(VisaDevice(resource_name, timeout_ms=timeout_ms))

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
                frequency_hz = _parse_display_c_number(
                    frequency_snapshot.display_c,
                    expected_unit_codes={"K"},
                    parameter_name="spot frequency",
                ) * 1000.0
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

    def configure(
        self,
        *,
        # Test signal
        frequency_hz: float | None = None,
        bias_voltage_v: float | None = None,
        osc_level_v: float | None = None,
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

        circuit_mode:
            How the instrument interprets L and C displays.
            Accepted values:
            - ``"auto"``
            - ``"series"``
            - ``"parallel"``

            Sent as raw command ``C1``, ``C2``, or ``C3`` from table 3-23.
            `ping()` reports circuit mode only when it can be inferred from the
            current DISPLAY A readback, for example ``LS`` or ``CP``.

        display_a, display_b:
            High-level measurement display selection.
            If either keyword is provided, both must be provided together.

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
        """

        commands: list[str] = []
        latest_display_c_recall_code: str | None = None

        if frequency_hz is not None:
            commands.append(_format_spot_frequency_set_command(_validate_frequency_hz(frequency_hz)))
            latest_display_c_recall_code = "FRR"

        if bias_voltage_v is not None:
            commands.append(_format_spot_bias_set_command(_validate_bias_voltage_v(bias_voltage_v)))
            latest_display_c_recall_code = "BIR"

        if osc_level_v is not None:
            commands.append(_format_osc_level_set_command(_validate_osc_level_v(osc_level_v)))
            latest_display_c_recall_code = "OLR"

        if circuit_mode is not None:
            commands.append(_get_circuit_mode_code(circuit_mode))

        if display_a is not None or display_b is not None:
            if display_a is None or display_b is None:
                raise ValueError("display_a and display_b must be provided together")
            commands.extend(_get_display_pair_codes(display_a, display_b))

        for command in commands:
            self._device.write(command)

        if latest_display_c_recall_code is not None:
            self._device.write(latest_display_c_recall_code)

    def close(self) -> None:
        """
        Close the VISA connection to the instrument.
        """

        self._device.close()

    def _read_display_c_number(
        self,
        recall_code: str,
        *,
        expected_unit_codes: set[str],
        parameter_name: str,
    ) -> float:
        snapshot = self._read_output_snapshot(recall_code)
        return _parse_display_c_number(
            snapshot.display_c,
            expected_unit_codes=expected_unit_codes,
            parameter_name=parameter_name,
        )

    def _read_output_snapshot(self, recall_code: str) -> _OutputSnapshot:
        """
        Read one DISPLAY A/B/C output snapshot.

        Manual basis:
        - Table 3-23: ``F1`` selects DISPLAY A/B/C output.
        - Table 3-23: recall codes such as ``FRR``, ``BIR``, and ``OLR`` choose
          which parameter is shown on DISPLAY C.
        - Table 3-23: ``EX`` triggers the output.
        - Figure 3-36 and table 3-25 define the returned data format.

        Important:
        - Do not send VISA device clear here. On the real instrument in this lab
          setup, device clear reset the frequency to 100 kHz.
        """

        self._device.write("F1")
        self._device.write(recall_code)
        self._device.write("EX")

        raw = self._device.read().strip()
        if not raw:
            raise RuntimeError("instrument returned no data")

        return _parse_output_snapshot(raw)


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


def _parse_display_field(field: str, *, display_name: str) -> _DisplayField:
    if len(field) < 5:
        raise RuntimeError(f"{display_name} field was too short: {field!r}")

    return _DisplayField(
        status_code=field[0],
        function_code=field[1:3],
        deviation_mode_code=field[3],
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

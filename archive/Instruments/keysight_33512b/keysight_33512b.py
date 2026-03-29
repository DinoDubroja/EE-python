"""
Minimal SCPI driver skeleton for Keysight 33512B.
"""

from __future__ import annotations

import math

from .transports import ScpiTransport


class Keysight33512B:
    """
    Base driver that sends SCPI commands through a transport.

    Model-specific waveform/channel commands will be added incrementally.
    """

    def __init__(self, transport: ScpiTransport):
        self._transport = transport

    def identify(self) -> str:
        """
        Return instrument identity string.
        """
        return self._transport.query("*IDN?")

    def reset(self) -> None:
        """
        Reset instrument state.
        """
        self._transport.write("*RST")

    def clear_status(self) -> None:
        """
        Clear instrument status/event registers.
        """
        self._transport.write("*CLS")

    def get_error(self) -> str:
        """
        Return one entry from the instrument error queue.
        """
        return self._transport.query("SYST:ERR?")

    def set_output(self, enabled: bool, channel: int = 1) -> None:
        """
        Placeholder output control.
        """
        _validate_channel(channel)
        state = "ON" if enabled else "OFF"
        self._transport.write(f"OUTP{channel} {state}")

    def set_waveform(self, shape: str, channel: int = 1) -> None:
        """
        Placeholder waveform selection.
        """
        _validate_channel(channel)
        waveform = shape.strip().upper()
        if not waveform:
            raise ValueError("shape must be a non-empty string")
        self._transport.write(f"SOUR{channel}:FUNC {waveform}")

    def set_frequency_hz(self, frequency_hz: float, channel: int = 1) -> None:
        """
        Set output frequency in Hz.
        """
        _validate_channel(channel)
        value = _validate_real("frequency_hz", frequency_hz)
        if value <= 0.0:
            raise ValueError("frequency_hz must be > 0")
        self._transport.write(f"SOUR{channel}:FREQ {value}")

    def set_amplitude_vpp(self, amplitude_vpp: float, channel: int = 1) -> None:
        """
        Set output amplitude in Vpp.
        """
        _validate_channel(channel)
        value = _validate_real("amplitude_vpp", amplitude_vpp)
        if value <= 0.0:
            raise ValueError("amplitude_vpp must be > 0")
        self._transport.write(f"SOUR{channel}:VOLT {value}")

    def set_offset_v(self, offset_v: float, channel: int = 1) -> None:
        """
        Set output DC offset in volts.
        """
        _validate_channel(channel)
        value = _validate_real("offset_v", offset_v)
        self._transport.write(f"SOUR{channel}:VOLT:OFFS {value}")

    def set_phase_deg(self, phase_deg: float, channel: int = 1) -> None:
        """
        Set output phase in degrees.
        """
        _validate_channel(channel)
        value = _validate_real("phase_deg", phase_deg)
        self._transport.write(f"SOUR{channel}:PHAS {value}")

    def close(self) -> None:
        """
        Close transport resources.
        """
        self._transport.close()


def _validate_channel(channel: int) -> None:
    if channel not in (1, 2):
        raise ValueError("channel must be 1 or 2")


def _validate_real(name: str, value: float) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be a real number, not bool")

    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be a real number") from exc

    if not math.isfinite(parsed):
        raise ValueError(f"{name} must be finite")

    return parsed

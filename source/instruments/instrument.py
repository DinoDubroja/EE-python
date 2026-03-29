"""
Shared instrument structures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import re


@dataclass(slots=True)
class ConnectionInfo:
    """
    Human-readable connection details derived from a VISA resource name.
    """

    resource_name: str
    interface: str
    visa_board: str | None = None
    host: str | None = None
    gpib_bus: int | None = None
    gpib_address: int | None = None
    socket_port: int | None = None

    def as_rows(self) -> list[tuple[str, str]]:
        rows = [("resource", self.resource_name)]
        if self.host is not None:
            rows.append(("IP address", self.host))
        if self.gpib_bus is not None:
            rows.append(("GPIB bus", str(self.gpib_bus)))
        if self.gpib_address is not None:
            rows.append(("GPIB address", str(self.gpib_address)))
        if self.socket_port is not None:
            rows.append(("socket port", str(self.socket_port)))
        return rows


def parse_visa_resource_name(resource_name: str) -> ConnectionInfo:
    """
    Parse common VISA resource name patterns into connection details.
    """

    text = resource_name.strip()
    parts = text.split("::")
    if not parts:
        return ConnectionInfo(resource_name=text, interface="unknown")

    board = parts[0]
    board_upper = board.upper()

    gpib_match = re.fullmatch(r"GPIB(\d+)", board_upper)
    if gpib_match and len(parts) >= 2 and parts[1].isdigit():
        return ConnectionInfo(
            resource_name=text,
            interface="direct GPIB",
            visa_board=board,
            gpib_bus=int(gpib_match.group(1)),
            gpib_address=int(parts[1]),
        )

    if board_upper.startswith("TCPIP"):
        host = parts[1] if len(parts) >= 2 else None
        info = ConnectionInfo(
            resource_name=text,
            interface="TCP/IP",
            visa_board=board,
            host=host,
        )

        if len(parts) >= 3:
            gateway_match = re.fullmatch(r"gpib(\d+),(\d+)", parts[2], re.IGNORECASE)
            if gateway_match:
                info.interface = "TCP/IP to GPIB gateway"
                info.gpib_bus = int(gateway_match.group(1))
                info.gpib_address = int(gateway_match.group(2))
                return info

            if parts[2].isdigit():
                info.interface = "TCP/IP socket"
                info.socket_port = int(parts[2])
                return info

        return info

    return ConnectionInfo(
        resource_name=text,
        interface=board,
        visa_board=board,
    )


@dataclass(slots=True)
class InstrumentReport:
    """
    Readable report produced by ping().
    """

    instrument_name: str
    connection: ConnectionInfo
    sections: list[tuple[str, dict[str, object]]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        lines = [self.instrument_name, ""]
        lines.append("Connection")
        for key, value in self.connection.as_rows():
            lines.append(f"  {key}: {_format_value(value)}")

        for title, rows in self.sections:
            if not rows:
                continue
            lines.append("")
            lines.append(title)
            for key, value in rows.items():
                lines.append(f"  {key}: {_format_value(value)}")

        if self.notes:
            lines.append("")
            lines.append("Notes")
            for note in self.notes:
                lines.append(f"  - {note}")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_text()


def _format_value(value: object) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "on" if value else "off"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


class ConfigurationVerificationError(RuntimeError):
    """
    Raised when a configure() self-check disagrees with instrument readback.
    """


def format_configure_success(
    instrument_name: str,
    parameter_name: str,
    actual_value: str,
) -> str:
    """
    Return the standard confirmation line for an exact or accepted setting.
    """

    return f"{instrument_name} | {parameter_name} -> {actual_value}"


def format_configure_adjusted(
    instrument_name: str,
    parameter_name: str,
    requested_value: str,
    actual_value: str,
) -> str:
    """
    Return the standard confirmation line for an adjusted setting.
    """

    return (
        f"{instrument_name} | {parameter_name} requested {requested_value} "
        f"-> instrument set {actual_value}"
    )


def format_configure_unverified(
    instrument_name: str,
    parameter_name: str,
    requested_value: str,
) -> str:
    """
    Return the standard confirmation line when readback is unavailable.
    """

    return (
        f"{instrument_name} | {parameter_name} requested {requested_value} "
        "-> readback unavailable"
    )


class Instrument(ABC):
    """
    Common base class for active instrument APIs.
    """

    def __init__(self, instrument_name: str, resource_name: str):
        self.instrument_name = instrument_name
        self.connection_info = parse_visa_resource_name(resource_name)

    @abstractmethod
    def ping(self, *, show: bool = True) -> InstrumentReport:
        """
        Return a readable report of the instrument's current situation.
        """

    @abstractmethod
    def configure(self, *args: object, **kwargs: object) -> object:
        """
        Change instrument state through a single entry point.

        Repo rule:
        configure() should verify requested changes against instrument readback
        when the instrument offers a safe readback path.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Release instrument resources.
        """

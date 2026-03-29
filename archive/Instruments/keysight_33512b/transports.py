"""
SCPI transport abstractions for instrument communication backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ScpiTransport(ABC):
    """
    Minimal transport interface used by SCPI drivers.
    """

    @abstractmethod
    def write(self, command: str) -> None:
        """
        Send a command that does not return a value.
        """

    @abstractmethod
    def query(self, command: str) -> str:
        """
        Send a command and return the response string.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Release backend resources.
        """


class VisaTransport(ScpiTransport):
    """
    PyVISA-backed transport.

    Notes:
    - This is intentionally minimal for now.
    - It raises an actionable error if pyvisa is not installed.
    """

    def __init__(self, resource_name: str, timeout_ms: int = 5000):
        try:
            import pyvisa
        except ImportError as exc:
            raise ImportError(
                "pyvisa is required for VisaTransport. Install with: pip install pyvisa"
            ) from exc

        rm = pyvisa.ResourceManager()
        self._resource = rm.open_resource(resource_name)
        self._resource.timeout = timeout_ms

    def write(self, command: str) -> None:
        self._resource.write(command)

    def query(self, command: str) -> str:
        return self._resource.query(command).strip()

    def close(self) -> None:
        self._resource.close()


class MockTransport(ScpiTransport):
    """
    In-memory transport for tests.
    """

    def __init__(self):
        self.writes = []
        self.query_map = {}
        self.queries = []

    def set_query_response(self, command: str, response: str) -> None:
        self.query_map[command] = response

    def write(self, command: str) -> None:
        self.writes.append(command)

    def query(self, command: str) -> str:
        self.queries.append(command)
        return self.query_map.get(command, "")

    def close(self) -> None:
        return None

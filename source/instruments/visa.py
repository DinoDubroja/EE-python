"""
PyVISA access and a minimal mock device.
"""

from __future__ import annotations


class VisaDevice:
    """
    Thin wrapper around a VISA resource.
    """

    def __init__(
        self,
        resource_name: str,
        *,
        timeout_ms: int = 5000,
        backend: str | None = None,
        resource_manager: object | None = None,
        resource: object | None = None,
        read_termination: str | None = None,
        write_termination: str | None = None,
    ):
        if resource is not None:
            self._resource_manager = resource_manager
            self._resource = resource
            self._owns_resource_manager = False
            self.resource_name = getattr(resource, "resource_name", resource_name)
        else:
            try:
                import pyvisa
            except ImportError as exc:
                raise ImportError(
                    "pyvisa is required for VisaDevice. Install with: pip install pyvisa"
                ) from exc

            if resource_manager is None:
                try:
                    if backend is None:
                        resource_manager = pyvisa.ResourceManager()
                    else:
                        resource_manager = pyvisa.ResourceManager(backend)
                except Exception as exc:
                    raise RuntimeError(
                        "Could not open a VISA resource manager. "
                        "Check that a VISA backend is installed and working."
                    ) from exc
                self._owns_resource_manager = True
            else:
                self._owns_resource_manager = False

            self._resource_manager = resource_manager
            self._resource = self._resource_manager.open_resource(resource_name)
            self.resource_name = resource_name

        self._resource.timeout = timeout_ms
        if read_termination is not None and hasattr(self._resource, "read_termination"):
            self._resource.read_termination = read_termination
        if write_termination is not None and hasattr(self._resource, "write_termination"):
            self._resource.write_termination = write_termination

    def write(self, message: str) -> None:
        self._resource.write(message)

    def read(self) -> str:
        return str(self._resource.read()).strip()

    def query(self, message: str) -> str:
        return str(self._resource.query(message)).strip()

    def clear(self) -> None:
        if hasattr(self._resource, "clear"):
            self._resource.clear()

    def read_stb(self) -> int | None:
        if hasattr(self._resource, "read_stb"):
            return int(self._resource.read_stb())
        return None

    def close(self) -> None:
        self._resource.close()
        if self._owns_resource_manager and hasattr(self._resource_manager, "close"):
            self._resource_manager.close()


class MockVisaDevice:
    """
    In-memory VISA-like device for local smoke checks.
    """

    def __init__(self, resource_name: str = "GPIB0::17::INSTR"):
        self.resource_name = resource_name
        self.timeout = 5000
        self.status_byte = 0
        self.writes: list[str] = []
        self._reads: list[str] = []

    def queue_read(self, message: str) -> None:
        self._reads.append(message)

    def write(self, message: str) -> None:
        self.writes.append(message)

    def read(self) -> str:
        if not self._reads:
            return ""
        return self._reads.pop(0).strip()

    def query(self, message: str) -> str:
        self.write(message)
        return self.read()

    def clear(self) -> None:
        return None

    def read_stb(self) -> int:
        return self.status_byte

    def close(self) -> None:
        return None

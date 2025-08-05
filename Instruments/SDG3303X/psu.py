from abc import ABC, abstractmethod
import pyvisa

class PSU(ABC):
    def __init__(self, address: str):
        self.address = address
        self.rm = None
        self.inst = None
    
    def connect(self):
        """Connect to the power supply."""
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(self.address)
        self.inst.timeout = 10000
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'
    
    def disconnect(self):
        if self.inst: self.inst.close()
        if self.rm:   self.rm.close()

    def identify(self) -> str:
        """Return the identification string of the power supply."""
        if not self.inst:
            raise RuntimeError("Instrument not connected.")
        return self.inst.query("*IDN?").strip()

    def __del__(self):
        """Ensure the connection is closed when the object is deleted."""
        self.disconnect()


    @abstractmethod
    def set_voltage(self, voltage: float, channel: int = 1):
        """Set the voltage limit on the given channel."""
        pass

    @abstractmethod
    def set_current(self, current: float, channel: int = 1):
        """Set the current limit on the given channel."""
        pass

    @abstractmethod
    def output_on(self, channel: int = 1):
        """Enable the output on the given channel."""
        pass

    @abstractmethod
    def output_off(self, channel: int = 1):
        """Disable the output on the given channel."""
        pass

    @abstractmethod
    def measure_voltage(self, channel: int = 1) -> float:
        """Return the measured voltage."""
        pass

    @abstractmethod
    def measure_current(self, channel: int = 1) -> float:
        """Return the measured current."""
        pass
    
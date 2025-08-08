from .psu import PSU

class SDS3303X(PSU):
    """
    SDS3303X Power Supply Unit Interface
    -------
    This class provides an interface to control and measure the SDS3303X programmable power supply.
    It allows setting voltage and current limits, configuring output modes, enabling/disabling output channels,
    and measuring voltage, current, and power on specified channels.
    Methods

    
    set_voltage(voltage: float, channel: int = 1)
        Set the voltage limit on the specified channel.
    set_current(current: float, channel: int = 1)
        Set the current limit on the specified channel.
    set_mode(mode: str = "default")
        Set the output mode of the power supply. Supported modes: 'default', 'series', 'parallel'.
    output_on(channel: int = 1)
        Enable the output on the specified channel.
    output_off(channel: int = 1)
        Disable the output on the specified channel.
    measure_voltage(channel: int = 1) -> float
        Measure and return the voltage on the specified channel, rounded to 4 decimal places.
    measure_current(channel: int = 1) -> float
        Measure and return the current on the specified channel, rounded to 4 decimal places.
    measure_power(channel: int = 1) -> float
        Measure and return the power on the specified channel, rounded to 4 decimal places.
    """
    
    def set_voltage(self, voltage: float, channel: int = 1):
        """Set the voltage limit on the given channel."""
        self.inst.write(f"CH{channel}:VOLTage {voltage}")

    def get_voltage(self, channel: int = 1) -> float:
        """Get the voltage limit on the given channel."""
        value = float(self.inst.query(f"CH{channel}:VOLTage?"))
        return round(value, 4)
        
    def set_current(self, current: float, channel: int = 1):
        """Set the current limit on the given channel."""
        self.inst.write(f"CH{channel}:CURRent {current}")

    def get_current(self, channel: int = 1) -> float:
        """Get the current limit on the given channel."""
        value = float(self.inst.query(f"CH{channel}:CURRent?"))
        return round(value, 4)
    
    def set_mode(self, mode: str = "default"):
        """Set the mode of the power supply."""
        if mode == "default":
            self.inst.write("OUTPut:TRACK 0")
        elif mode == "series":
            self.inst.write("OUTPut:TRACK 1")
        elif mode == "parallel":
            self.inst.write("OUTPut:TRACK 2")
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'default', 'series', or 'parallel'.")
        
    
    def output_on(self, channel: int = 1):
        """Enable the output on the given channel."""
        self.inst.write(f"OUTPut CH{channel},ON")

    def output_off(self, channel: int = 1):
        """Disable the output on the given channel."""
        self.inst.write(f"OUTPut CH{channel},OFF")
    
    def measure_voltage(self, channel: int = 1) -> float:
        """Return the measured voltage rounded to 4 decimal places."""
        value = float(self.inst.query(f"MEASure:VOLTage? CH{channel}"))
        return round(value, 4)
    
    def measure_current(self, channel: int = 1) -> float:
        """Return the measured current rounded to 4 decimal places."""
        value = float(self.inst.query(f"MEASure:CURRent? CH{channel}"))
        return round(value, 4)
    
    def measure_power(self, channel: int = 1) -> float:
        """Return the measured power rounded to 4 decimal places."""
        value = float(self.inst.query(f"MEASure:POWer? CH{channel}"))
        return round(value, 4)
    
    
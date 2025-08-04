

def set_output(
        self,
        channel: int = 1,
        load: str = "HiZ",
        polarity: str = "normal",
        snr: float = None
    ) -> None:
        """
        Configure the output settings for a given channel.

        Args:
            channel (int): Channel number (1 or 2).
            load (str, optional): Load type, either 'HiZ' or '50'. Defaults to 'HiZ'.
            polarity (str, optional): Output polarity, 'normal' or 'inverted'. Defaults to 'normal'.
            snr (float, optional): Signal-to-noise ratio; must be between 2.1 and 1e9.  
                If omitted, noise addition is turned off.

        Raises:
            ValueError: If `load` or `polarity` is invalid, or if `snr` is out of range.
        """
        # Set the output load type
        print("DEBUG load repr:", repr(load))
        if load not in ["HiZ", "50"]:
            raise ValueError("Invalid load type. Use 'HiZ' or '50'.")
        elif load == "50":
            self.inst.write(f"C{channel}:OUTP LOAD")
            print("DEBUG set load to 50")
        elif load == "HiZ":
            self.inst.write(f"C{channel}:OUTP LOAD, HZ")
            print("DEBUG set load to HiZ")

        # Set the output polarity 
        if polarity not in ["normal", "inverted"]:
            raise ValueError("Invalid polarity. Use 'normal' or 'inverted'.")
        elif polarity == "normal":
            self.inst.write(f"C{channel}:OUTP POLarity,NORMal")
        elif polarity == "inverted":
            self.inst.write(f"C{channel}:OUTP POLarity,INVerted")

        # SNR is optional; if provided, it must be between 2.1 and 1,000,000,000
        
        if snr is not None and (snr < 2.1 or snr > 1000000000):
            raise ValueError("SNR must be between 2.1 and 1,000,000,000.")
        elif snr is not None:
            self.inst.write(f"C{channel}:NOISE_ADD STATE,ON,RATIO,{snr}")
        else:
            self.inst.write(f"C{channel}:NOISE_ADD STATE,OFF")

def waveform(
        self,
        wave_type: str,
        frequency: float = None,
        period: float = None,
        duty_cycle: float = None,
        amplitude: float = None,
        amplitude_rms: float = None,
        amplitude_dbm: float = None,
        offset: float = 0.0,
        symmetry: float = None,
        duty: float = None,
        phase: float = 0.0,
        stdev: float = None,
        mean: float = None,
        # Only used for pulse waveforms
        pulse_width: float = None,
        pulse_rise: float = None,
        pulse_fall: float = None,
        pulse_delay: float = None,
        
        high_level: float = None,
        low_level: float = None,
        bandwidth_limit: bool = False,
        bandwidth: float = None,


        channel: int = 1
    ):
        # Wafeform type
        if wave_type not in ["SINE", "SQUARE", "RAMP", "PULSE", "DC", "NOISE", "ARB"]:
            raise ValueError(f"Invalid wave type '{wave_type}'. Must be one of: "
                             "SINE, SQUARE, RAMP, PULSE, DC, NOISE, ARB.")
        else:
            self.inst.write(f"C{channel}:BSWV WVTP,{wave_type}")
        
        # Frequency and period
        if frequency == None and period == None:
            raise ValueError("Either frequency or period must be specified.")
        elif frequency is not None and period is not None:
            raise ValueError("Specify either frequency or period, not both.")
        elif frequency is not None and frequency <= 0:
            raise ValueError("Frequency must be a positive number.")
        elif period is not None and period <= 0:
            raise ValueError("Period must be a positive number.")
        elif frequency is not None:
            self.inst.write(f"C{channel}:BSWV FRQ,{frequency}")
        elif period is not None:
            self.inst.write(f"C{channel}:BSWV PERI,{period}")

        # Amplitude and offset
        if high_level is not None and low_level is not None:
            if high_level <= low_level:
                raise ValueError("High level must be greater than low level.")
            amplitude = (high_level - low_level) / 2
            offset = (high_level + low_level) / 2

        if amplitude == None and amplitude_rms == None and amplitude_dbm == None:
            raise ValueError("One of amplitude, amplitude_rms, or amplitude_dbm must be specified.")
        elif amplitude is not None:
            self.inst.write(f"C{channel}:BSWV AMP,{amplitude}")
        elif amplitude_rms is not None:
            self.inst.write(f"C{channel}:BSWV AMPVRMS,{amplitude_rms}")
        elif amplitude_dbm is not None:
            self.inst.write(f"C{channel}:BSWV AMPDBM,{amplitude_dbm}")

        if offset is not None:
            self.inst.write(f"C{channel}:BSWV OFST,{offset}")   

        # Symmetry
        if symmetry is not None and wave_type == "RAMP":
            if not (0 <= symmetry <= 100):
                raise ValueError("Symmetry must be between 0 and 100.")
            self.inst.write(f"C{channel}:BSWV SYM,{symmetry}")

        # Duty cycle
        if duty_cycle is not None and wave_type == ("SQUARE" or "PULSE"):
            if not (0 <= duty_cycle <= 100):
                raise ValueError("Duty cycle must be between 0 and 100.")
            self.inst.write(f"C{channel}:BSWV DUTY,{duty_cycle}")

        # Phase
        if phase is not None:
            if not (0 <= phase < 360):
                raise ValueError("Phase must be between 0 and 360 degrees.")
            self.inst.write(f"C{channel}:BSWV PHSE,{phase}")

        ## TO BE IMPLEMENTED   
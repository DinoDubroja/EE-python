from . import utils

class Waveform:

        def __init__(self, parent, channel: int = 1):
            self.channel = channel
            self._parent = parent
        
        def sine(
                self, 
                frequency: float, 
                amplitude: float = 1.0,
                offset: float = 0.0,
                phase: float = 0.0,
                high_level: float = None,
                low_level: float = None
                ):
            utils.waveform(self._parent, frequency=frequency, amplitude=amplitude, offset=offset,channel=self.channel, 
                    phase=phase, wave_type="SINE", high_level=high_level, low_level=low_level)
            
        def square(
                self,
                frequency: float,
                amplitude: float = 1.0,
                offset: float = 0.0,
                duty_cycle: float = 50.0,
                phase: float = 0.0,
                high_level: float = None,
                low_level: float = None
                ):
            utils.waveform(self, frequency=frequency, amplitude=amplitude, offset=offset, channel=self.channel, 
                    phase=phase, wave_type="SQUARE", duty_cycle=duty_cycle, high_level=high_level, low_level=low_level)
            
        def ramp(
                self,
                frequency: float,
                amplitude: float = 1.0,
                offset: float = 0.0,
                symmetry: float = 50.0,
                phase: float = 0.0,
                high_level: float = None,
                low_level: float = None
                ):
            utils.waveform(self, frequency=frequency, amplitude=amplitude, offset=offset, channel=self.channel, 
                    phase=phase, wave_type="RAMP", symmetry=symmetry, high_level=high_level, low_level=low_level)
        
        def triangle(
                self,
                frequency: float,
                amplitude: float = 1.0,
                offset: float = 0.0,
                phase: float = 0.0,
                high_level: float = None,
                low_level: float = None
            ):
            utils.waveform(self, frequency=frequency, amplitude=amplitude, offset=offset, channel=self.channel, 
                    phase=phase, wave_type="RAMP",symmetry=50, high_level=high_level, low_level=low_level)

        def sawtooth(
                self,
                frequency: float,
                amplitude: float = 1.0,
                offset: float = 0.0,
                phase: float = 0.0,
                high_level: float = None,
                low_level: float = None
            ):
            utils.waveform(self, frequency=frequency, amplitude=amplitude, offset=offset, channel=self.channel, 
                    phase=phase, wave_type="RAMP",symmetry=0, high_level=high_level, low_level=low_level)
            
        def on(self):
            self._parent.inst.write(f"C{self.channel}:OUTP ON")
        
        def off(self):
            self._parent.inst.write(f"C{self.channel}:OUTP OFF")

        def modulation(
                self,
                type: str = "AM",
                source: str = "INT",
                frequency: float = 1000.0,
                depth: float = 50.0,
                waveform: str = "SINE",
                deviation: float = 0.0,
                hop_frequency: float = None
        ):
            
                if type not in ["AM", "FM", "PM", "FSK", "ASK", "PSK", "DSBAM", "PWM"]:
                        raise ValueError("Invalid modulation type. Choose from AM, FM, PM, FSK, ASK, PSK, DSBAM, PWM.")
                
                if source not in ["internal", "external"]:
                        raise ValueError("Invalid modulation source. Choose from internal or external.")
                
                if waveform not in ["SINE", "SQUARE", "TRIANGLE", "UPRAMP", "DNRAMP", "NOISE", "ARB"]:
                        raise ValueError("Invalid waveform type. Choose from SINE, SQUARE, TRIANGLE, UPRAMP, DNRAMP, NOISE, ARB.")
                
                if hop_frequency == None:
                      hop_frequency = frequency
                
                if type == "AM":
                        self._parent.inst.write(f"C{self.channel}:MDWV {type},MDSP,{waveform},FRQ,{frequency},DEPTH,{depth},SRC,{source}")
                        print(f"AM, {self.channel}")
                if type == "FM":
                        self._parent.inst.write(f"C{self.channel}:MDWV {type},MDSP,{waveform},FRQ,{frequency},DEVI,{deviation},SRC,{source}")
                if type == "PM":
                        self._parent.inst.write(f"C{self.channel}:MDWV {type},MDSP,{waveform},FRQ,{frequency},DEVI,{deviation},SRC,{source}")
                if type == "PWM":
                        self._parent.inst.write(f"C{self.channel}:MDWV {type},MDSP,{waveform},FRQ,{frequency},DEVI,{deviation},SRC,{source}")
                if type == "ASK":
                        self._parent.inst.write(f"C{self.channel}:MDWV {type},KFRQ,{frequency},SRC,{source}")
                if type == "FSK":
                        self._parent.inst.write(f"C{self.channel}:MDWV {type},KFRQ,{frequency},HRFQ,{hop_frequency},SRC,{source}")
                if type == "PSK":
                        self._parent.inst.write(f"C{self.channel}:MDWV {type},KFRQ,{frequency},SRC,{source}")
                
                
        def modulation_on(self):
              self._parent.inst.write(f"C{self.channel}:MDWV STATE,ON")

        def modulation_off(self):
              self._parent.inst.write(f"C{self.channel}:MDWV STATE,OFF")

        def sweep(
                self,
                sweep_time: float = 2,
                start_freq: float = 1000,
                stop_freq: float = 10000,
                mode: str = "LINE",
                direction: str = "UP",
                trig_source: str = "INT"
        ):
                self._parent.inst.write(f"C{self.channel}:SWWV TIME,{sweep_time},START,{start_freq},STOP,{stop_freq},SWMD,{mode},DIR,{direction},TRSR,{trig_source}")

        def sweep_on(self):
              self._parent.inst.write(f"C{self.channel}:SWWV STATE,ON")

        def sweep_off(self):
              self._parent.inst.write(f"C{self.channel}:SWWV STATE,OFF")

        def burst(
                self,
                period: float = 1,
                start_phase: float = 0,
                mode: str = "NCYC",
                trig_source: str = "INT",
                cycles: int = 1,
        ):
                self._parent.inst.write(f"C{self.channel}:BTWV PRD,{period},STPS,{start_phase},GATE_NCYC,{mode},TRSR,{trig_source},TIME,{cycles}")

        def burst_on(self):
              self._parent.inst.write(f"C{self.channel}:BTWV STATE,ON")
        
        def burst_off(self):
              self._parent.inst.write(f"C{self.channel}:BTWV STATE,OFF")


         
        

            

        
        
            

            

                
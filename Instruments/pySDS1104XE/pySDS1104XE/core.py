import pyvisa as visa
import logging
import time

class SDS1104XE:

    def __init__(self, resource_name: str):
        """
        resource_name: VISA resource string, e.g. 'TCPIP0::192.168.0.10::5025::SOCKET'
        """
        self.rm = visa.ResourceManager()
        
        self.inst = self.rm.open_resource(resource_name)
        self.inst.timeout = 5000
        self.inst.write_termination = '\n'
        self.inst.read_termination = '\n'

        self.inst.write("CHDR OFF")

    def identify(self) -> str:
        """*IDN? → manufacturer,model,serial,firmware"""
        return self.inst.query("*IDN?").strip()

    def reset(self):
        """Soft reset (same as front-panel Default)."""
        self.inst.write("*RST")

    def configure_acquisition(self, mode: str='SAMPLING',
                              average_count: int=None,
                              memory: str=None):
        
        mode = mode.upper()

        if mode not in ["SAMPLING","PEAK_DETECT","AVERAGE", "HIGH_RES"]:
            raise ValueError("Invalid acquisition mode.")
        
        if average_count is not None:
            if average_count not in [4, 16, 32, 64, 128, 256, 512, 1024]:
                raise ValueError("Invalid average count.")
        
        # Set the memory depth
        if memory is not None:
            self.inst.write(f"MSIZ {memory}")
        
        if mode == "AVERAGE":
            self.inst.write(f"ACQW AVERAGE,{average_count}")
        elif mode == "SAMPLING":
            self.inst.write(f"ACQW SAMPLING")
        elif mode == "PEAK_DETECT":
            self.inst.write(f"ACQW PEAK_DETECT")
        elif mode == "HIGH_RES":
            self.inst.write(f"ACQW HIGH_RES")

    def configure_channel(self,channel: int, range: float, probe: int=1, 
                          coupling: str = 'D1M', offset: float=0.0, skew: float = 0.0,
                          bw_limit: bool=False, invert: bool=False):
        
        
        if channel not in [1,2,3,4]:
            raise ValueError("Channel must be 1,2,3 or 4.")
        if probe not in [0.1,0.2,0.5,1,2,5,10,20,50,100,200,500,1000,2000,5000,10000]:
            raise ValueError("Probe must be between 0.1 and 10000")
        if coupling not in ["D1M", "A1M", "GND"]:
            print(coupling)
            raise ValueError("Invalid coupling.")
        
        time.sleep(0.1)
        if bw_limit:
            self.inst.write(f"BWL C{channel},ON")
        else:
            self.inst.write(f"BWL C{channel},OFF")
        time.sleep(0.1)
        if invert:
            self.inst.write(f"C{channel}:INVS ON")
        else:
            self.inst.write(f"C{channel}:INVS OFF")
        time.sleep(0.1)

        self.inst.write(f"C{channel}:ATTN {probe}")
        time.sleep(0.1)
        self.inst.write(f"C{channel}:CPL {coupling}")
        time.sleep(0.1)
        self.inst.write(f"C{channel}:OFST {offset}")
        time.sleep(0.1)
        self.inst.write(f"C{channel}:SKEW {skew}")
        time.sleep(0.1)
        self.inst.write(f"C{channel}:VDIV {range}")
        time.sleep(0.1)
    
    

    def get_raw(self, channel: int) -> list[int]:
        """
        Fetch the full 8-bit signed waveform record for C{channel}.

        Uses:
        - CHDR OFF       — suppress text headers so the first byte is '#'
        - WFSU SP,0,NP,0,FP,0 — request every point, from the first sample on
        - <trace>:WF? DAT2 — retrieve the binary block of raw data
        
        Returns:
        List of signed ints in –128…+127 ready for scaling.
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1–4.")

        # Turn off the ASCII header so '#...' is at the very start
        self.inst.write("CHDR OFF")

        # Ask for every point in the buffer, no sparsing
        self.inst.write("WFSU SP,0,NP,0,FP,0")

        self.inst.clear()

        # Grab 8-bit data from the instrument
        raw = self.inst.query_binary_values(
            f"C{channel}:WF? DAT2",
            datatype='b',        # 'b' = signed 8-bit integers
            container=list       # return as a Python list
        )

        self.inst.clear()

        return raw
    
    def get_offset(self, channel: int) -> float:
        """
        Returns the offset voltage for channel C{channel}.
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1–4.")
        return float(self.inst.query(f"C{channel}:OFST?"))
    
    def get_volts_div(self, channel: int):
        """
        Returns the volts per division (range) for selectedchannel.
        """
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1–4.")
        return float(self.inst.query(f"C{channel}:VDIV?"))
    
    def get_sample_rate(self) -> float:
        """
        Returns the sample rate for selected channel.
        """
        return float(self.inst.query(f"SARA?"))
    
    def get_time_div(self):
        """
        Returns the time per division (range) for selected channel in seconds.
        """
        return float(self.inst.query(f"TDIV?"))
    
    def set_time_div(self, value) -> float:
        """
        Set horizontal scale (seconds/div) using SCPI TIME_DIV <value>.

        Args:
            value: seconds/div as float (in seconds) or string with units
                   like "10us", "2ms", "1S" (case-insensitive).

        Returns:
            float: the seconds/div that was actually sent (after snapping
                   to the nearest valid step).

        Notes:
            Valid steps per Siglent manual:
            1-2-5 sequence across units:
              ns: 1,2,5,10,20,50,100,200,500
              us: 1,2,5,10,20,50,100,200,500
              ms: 1,2,5,10,20,50,100,200,500
              s : 1,2,5,10,20,50,100
        """
        # --- parse input into seconds ---
        if isinstance(value, str):
            s = value.strip().lower()
            if s.endswith("ns"):
                sec = float(s[:-2]) * 1e-9
            elif s.endswith("us"):
                sec = float(s[:-2]) * 1e-6
            elif s.endswith("ms"):
                sec = float(s[:-2]) * 1e-3
            elif s.endswith("s"):
                sec = float(s[:-1])
            else:
                # treat bare number as seconds
                sec = float(s)
        else:
            sec = float(value)

        # --- build the allowed list in seconds ---
        decade = [1, 2, 5, 10, 20, 50, 100, 200, 500]
        allowed = (
            [x * 1e-9 for x in decade] +
            [x * 1e-6 for x in decade] +
            [x * 1e-3 for x in decade] +
            [x for x in [1, 2, 5, 10, 20, 50, 100]]
        )

        # --- snap to nearest valid step ---
        target = min(allowed, key=lambda a: abs(a - sec))

        # --- format with required unit suffix (no spaces) ---
        def token(seconds: float) -> str:
            # choose unit and integer-like mantissa for 1-2-5 steps
            if seconds < 1e-6:
                v = round(seconds / 1e-9)     # ns
                return f"{int(v)}NS"
            elif seconds < 1e-3:
                v = round(seconds / 1e-6)     # us
                return f"{int(v)}US"
            elif seconds < 1:
                v = round(seconds / 1e-3)     # ms
                return f"{int(v)}MS"
            else:
                # seconds only go up to 100S
                v = int(round(seconds))
                return f"{v}S"

        cmd = f"TIME_DIV {token(target)}"
        self.inst.write(cmd)                 # send SCPI
        return target


    def get_voltage(self, channel: int) -> list[float]:
        """
        Returns the voltage for selected channel.
        """
        raw    = self.get_raw(channel)           # e.g. [127, 126, ...]
        vdiv   = self.get_volts_div(channel)     # e.g. 1.0 V/div
        offset = self.get_offset(channel)        # e.g. 0.0 V

        scale = vdiv / 25                        # per-code volts

        volts = [
            code * scale - offset
            for code in raw
        ]
        return volts
    
    def capture(self, channel: int):
        v = self.get_voltage(channel)
        t = self.get_time(channel)
        return t, v
    
    def get_number_of_samples(self, channel: int) -> int:
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1–4.")
        return float(self.inst.query(f"SANU? C{channel}"))
    
    def get_time(self, channel: int) -> list[float]:
        if channel not in (1, 2, 3, 4):
            raise ValueError("Channel must be 1–4.")
        
        tdiv = self.get_time_div()
        sample_rate = self.get_sample_rate()
        t_0 = -(tdiv * 14) / 2
        dt = 1 / sample_rate
        times = []
        times.append(t_0)

        samples = self.get_number_of_samples(channel)
        for i in range(1, int(samples)):
            times.append(times[i-1] + dt)
        return times
    


    def set_trigger_mode(self, mode: str) -> str:
        """
        Set trigger mode.

        SCPI:
            TRMD <AUTO|NORM|SINGLE|STOP>
            TRMD?  -> returns current mode

        Args:
            mode: case-insensitive; accepts common synonyms:
                  "auto", "normal"/"norm", "single"/"single shot"/"single-shot", "stop"/"stopped".

        Returns:
            str: mode actually set as reported by the instrument (e.g., "AUTO", "NORM", "SINGLE", "STOP").
        """
        # normalize input (accept a few friendly aliases)
        s = str(mode).strip().lower().replace("_", " ").replace("-", " ")
        aliases = {
            "auto": "AUTO",
            "norm": "NORM",
            "normal": "NORM",
            "single": "SINGLE",
            "single shot": "SINGLE",
            "single shot ": "SINGLE",
            "stop": "STOP",
            "stopped": "STOP",
        }
        if s not in aliases:
            raise ValueError('mode must be one of: "auto", "normal", "single", "stop"')

        token = aliases[s]
        try:
            self.write(f"TRMD {token}")
        except AttributeError:
            # fallback if write/query wrappers don't exist
            self.inst.write(f"TRMD {token}")

        try:
            result = self.query("TRMD?").strip()
        except AttributeError:
            result = self.inst.query("TRMD?").strip()

        return result
    
  
    def set_trigger_edge(self, source: str, *, slope: str | None = None, hold: float | str | None = None) -> tuple[str, str | None]:
        """
        Configure Edge trigger (type+source via TRSE; slope via TRSL; optional holdoff via HT/TI/HV).

        SCPI per SDS1000X-E:
          TRSE EDGE,SR,<source>[,HT,TI,HV,<hold>]     # select type/source (+ optional holdoff)  [PG §TRIG_SELECT]
          <source>: C1|C2|C3|C4|LINE|EX|EX5 (four-ch units don’t have EX/EX5)                    [PG §TRIG_SELECT]
          Cn:TRSL <POS|NEG|WINDOW>                   # slope                                     [PG §TRIG_SLOPE]
        Holdoff limits (EDGE): 80 ns .. 1.5 s (datasheet)

        Returns:
          (trse_cmd, trsl_cmd or None)
        """
        src = str(source).strip().upper()
        valid_src = {"C1","C2","C3","C4","LINE","EX","EX5"}
        if src not in valid_src:
            raise ValueError(f"Invalid source {src}. Use one of {sorted(valid_src)}")

        parts = [f"TRSE EDGE,SR,{src}"]  # TRIG_SELECT syntax uses key-value pairs (SR=source)

        if hold is not None:
            seconds = self._to_seconds(hold)
            if not (80e-9 <= seconds <= 1.5):
                raise ValueError("Edge holdoff out of range (80 ns–1.5 s)")
            parts += ["HT","TI","HV", self._fmt_t(seconds)]  # HT=hold type, TI=time, HV=value
        else: parts += ["HT", "OFF"]

        trse_cmd = ",".join(parts)
        self.inst.write(trse_cmd)

        trsl_cmd = None
        if slope is not None:
            sl = str(slope).strip().upper()
            if sl not in {"POS","NEG","WINDOW"}:
                raise ValueError('slope must be "POS", "NEG", or "WINDOW"')
            # channel-scoped slope command (only valid for C1..C4/EX/EX5; not LINE)
            if src == "LINE":
                raise ValueError("Slope cannot be set on LINE source; choose a channel/EXT source")
            # Map EX/EX5 to the prefix used by the scope: EX for EXT, EX5 for EXT/5 in this programming guide
            prefix = src.replace("EXT","EX")  # if you pass EXT/EXT5 upstream, normalize to EX/EX5 here
            trsl_cmd = f"{prefix}:TRSL {sl}"
            self.inst.write(trsl_cmd)

        return trse_cmd, trsl_cmd

    # ---- helpers ----
    def _to_seconds(self, v) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().lower()
        if s.endswith("ns"): return float(s[:-2]) * 1e-9
        if s.endswith("us"): return float(s[:-2]) * 1e-6
        if s.endswith("ms"): return float(s[:-2]) * 1e-3
        if s.endswith("s"):  return float(s[:-1])
        return float(s)

    def _fmt_t(self, seconds: float) -> str:
        if seconds >= 1:       return f"{seconds:.9g}S"
        if seconds >= 1e-3:    return f"{seconds*1e3:.9g}MS"
        if seconds >= 1e-6:    return f"{seconds*1e6:.9g}US"
        return f"{seconds*1e9:.9g}NS"
    

    def set_trigger_level(self, source: str, level: float | str) -> str:
        """
        Set trigger level for the given source.

        SCPI: C#:TRLV <voltage>
        """
        src = source.strip().upper()
        valid_src = {"C1", "C2", "C3", "C4", "EX", "EX5"}
        if src not in valid_src:
            raise ValueError(f"Invalid source {src}. Use one of {sorted(valid_src)}")

        volts = self._to_volts(level)

        # enforce datasheet ranges (division range check)
        # we can't know volts/div here unless we query, so we only check absolute spec
        if src.startswith("C"):  # ±4.5 div, but without v/div we allow ±50 V safe limit
            max_v = 50
        else:  # EXT / EXT5
            max_v = 5  # typical for external trigger, adjust if datasheet says otherwise
        if not (-max_v <= volts <= max_v):
            raise ValueError(f"Level {volts} V out of safe range ±{max_v} V")

        cmd = f"{src}:TRLV {self._fmt_v(volts)}"
        self.inst.write(cmd)
        return cmd

    def set_trigger_coupling(self, source: str, coupling: str) -> str:
        """
        Set trigger coupling for the given source.

        SCPI: C#:TRCP <AC|DC|LFREJ|HFREJ>
        """
        src = source.strip().upper()
        valid_src = {"C1", "C2", "C3", "C4", "EX", "EX5"}
        if src not in valid_src:
            raise ValueError(f"Invalid source {src}. Coupling is not applicable to LINE source.")

        coup = coupling.strip().upper()
        if coup not in {"AC", "DC", "LFREJ", "HFREJ"}:
            raise ValueError(f"Invalid coupling {coup}")

        cmd = f"{src}:TRCP {coup}"
        self.inst.write(cmd)
        return cmd

    # --- helpers ---
    def _to_volts(self, v) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().lower()
        if s.endswith("mv"):
            return float(s[:-2]) * 1e-3
        if s.endswith("uv"):
            return float(s[:-2]) * 1e-6
        if s.endswith("v"):
            return float(s[:-1])
        return float(s)

    def _fmt_v(self, volts: float) -> str:
        if abs(volts) >= 1:
            return f"{volts:.9g}V"
        elif abs(volts) >= 1e-3:
            return f"{volts*1e3:.9g}MV"
        else:
            return f"{volts*1e6:.9g}UV"


            


        

        
       


    
        
        




        
            

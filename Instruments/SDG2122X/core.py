"""
sdg2122x.py

A Python class to control the Siglent SDG2122X Series Arbitrary Waveform Generator via VISA/SCPI.

Based on the “SDG Series Arbitrary Waveform Generator Programming Guide (PG02_E04A)” :contentReference[oaicite:25]{index=25}.
"""

import pyvisa
import utils
from .waveform import Waveform



class SDG2122X:

    def __init__(self, address: str):
        """
        Store the VISA address (e.g. "TCPIP0::192.168.1.100::5025::SOCKET").
        """
        self.address = address
        self.rm = None
        self.inst = None

        self.wave = Waveform(self, channel=1)  # Default to channel 1

    def channel(self, n):
        """
        Return a Waveform object for the specified channel (1 or 2).
        """
        if n not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return Waveform(self, channel=n)

    def __del__(self):
        """
        Ensure the VISA session is closed when the object is deleted.
        """
        self.disconnect()

    def connect(self):
        """
        Open a VISA session to the AWG and configure timeouts/terminations.
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(self.address)
        self.inst.timeout = 5000              # 5 s timeout
        self.inst.write_termination = '\n'
        self.inst.read_termination = '\n'

    def disconnect(self):
        """
        Close the VISA session cleanly.
        """
        if self.inst:
            self.inst.close()
            self.inst.clear()
            self.inst = None
        if self.rm:
            self.rm.close()
            self.rm = None

    def reset(self):
        """
        Factory-reset the AWG.
        """
        self.inst.write("*RST")

    def identify(self) -> str:
        """
        Return the instrument ID string.
        """
        return self.inst.query("*IDN?").strip()


            
    def query_waveform(self, channel: int = 1) -> str:
        """
        Read back the current basic waveform settings.
        """
        return self.inst.query(f"C{channel}:BSWV?").strip()
    
    

    def sweep(
        self,
        start_freq: float,
        stop_freq: float,
        sweep_time: float,
        mode: str = "LINE",
        direction: str = "UP",
        channel: int = 1
    ):
        """
        Configure a frequency sweep on the specified channel.
        SCPI:
          C{n}:SWWV START,{start_freq},STOP,{stop_freq},
                   TIME,{sweep_time},SWMD,{mode},DIR,{direction}
        See Section 3.6 :contentReference[oaicite:39]{index=39}
        """
        cmd = (f"C{channel}:SWWV START,{start_freq},STOP,{stop_freq},"
               f"TIME,{sweep_time},SWMD,{mode},DIR,{direction}")
        self.inst.write(cmd)



    def configure_burst(
        self,
        period: float,
        cycles: int,
        channel: int = 1
    ):
        """
        Configure a burst on the specified channel.
        SCPI:
          C{n}:BTWV PRD,{period},TIME,{cycles}
        See Section 3.7 :contentReference[oaicite:41]{index=41}
        """
        self.inst.write(f"C{channel}:BTWV PRD,{period},TIME,{cycles}")

    
    
    
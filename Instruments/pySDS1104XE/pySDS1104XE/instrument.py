import pyvisa as visa
import logging
from .waveform import WaveformParser

log = logging.getLogger(__name__)

class SDS1104XE:
    """
    Driver for Siglent SDS1104X-E Oscilloscope.
    """

    VALID_CHANNELS = {'C1','C2','C3','C4'}
    VALID_ACQ_MODES = {'SAMPLING','PEAK_DETECT','AVERAGE','HIGH_RES'}

    def __init__(self, resource_name: str):
        """
        resource_name: VISA resource string, e.g. 'TCPIP0::192.168.0.10::5025::SOCKET'
        """
        self.rm = visa.ResourceManager()
        
        self.inst = self.rm.open_resource(resource_name)
        self.inst.timeout = 5000
        self.inst.write_termination = '\n'
        self.inst.read_termination = '\n'

    def identify(self) -> str:
        """*IDN? → manufacturer,model,serial,firmware"""
        return self.inst.query("*IDN?").strip()

    def reset(self):
        """Soft reset (same as front-panel Default)."""
        self.inst.write("*RST")

    def set_channel(self, channel: str, *, coupling: str='D1M',
                    vdiv: float=1.0, offset: float=0.0,
                    attenuation: float=1.0):
        """
        Configure an analog channel:
         - coupling: one of 'A1M','A50','D1M','D50','GND'
         - vdiv: volts/div
         - offset: volts
         - attenuation: probe ratio (1,10,100, ...)
        """
        if channel not in self.VALID_CHANNELS:
            
        # coupling
        self.inst.write(f"{channel}:CPL {coupling}")
        # voltage/div
        self.inst.write(f"{channel}:VOLT_DIV {vdiv}")
        # offset
        self.inst.write(f"{channel}:OFFSET {offset}")
        # probe attenuation
        self.inst.write(f"{channel}:ATTENUATION {attenuation}")

    def configure_acquisition(self, mode: str='SAMPLING',
                              average_count: int=None,
                              memory_size: str=None):
        """
        mode: 'SAMPLING','PEAK_DETECT','AVERAGE','HIGH_RES' :contentReference[oaicite:6]{index=6}  
        average_count: integer if mode=='AVERAGE'  
        memory_size: e.g. '14M','1.4M' :contentReference[oaicite:7]{index=7}
        """
        mode = mode.upper()
        if mode not in self.VALID_ACQ_MODES:
            raise ValueError(f"Invalid acquisition mode: {mode

        cmd = f"ACQW {mode}"
        if mode=='AVERAGE' and average_count is not None:
            cmd += f",{average_count}"
        self.inst.write(cmd)
        if memory_size:
            self.inst.write(f"MSIZ {memory_size}")

    def get_waveform(self, channel: str):
        """
        Fetch primary waveform data from an analog channel.
        Returns: (time_axis: list[float], volts: list[float])
        Uses:
          • Set data format to BYTE or WORD
          • :WAV:PRE? → preamble
          • :WAV:DATA? → raw binary block
        See WAVEFORM commands :contentReference[oaicite:8]{index=8}
        """
        # select source
        self.inst.write(f"WAV:SOUR {channel}")
        # set format
        self.inst.write("WAV:FORM BYTE")
        self.inst.write("WAV:MODE RAW")
        # get preamble & parse
        pre = self.inst.query("WAV:PRE?").split(',')
        parser = WaveformParser(preamble=pre)
        # fetch raw bytes
        raw = self.inst.query_binary_values("WAV:DATA?", datatype='B', container=bytes)
        return parser.scale(raw)

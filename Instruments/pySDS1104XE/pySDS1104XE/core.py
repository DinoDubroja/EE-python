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
        • CHDR OFF       — suppress text headers so the first byte is '#'
        • WFSU SP,0,NP,0,FP,0 — request every point, from the first sample on
        • <trace>:WF? DAT2 — retrieve the binary block of raw data
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
            


        

        
       


    
        
        




        
            

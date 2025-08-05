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
        raw_codes = self.inst.query_binary_values(
            f"C{channel}:WF? DAT2",
            datatype='b',        # 'b' = signed 8-bit integers
            container=list       # return as a Python list
        )

        return raw_codes
       


        
    def get_waveform_chinese(self,channel: int):

        self.inst.write(f"CHDR OFF")
        time.sleep(0.1)

        vdiv = self.inst.query(f"C{channel}:VDIV?")
        time.sleep(0.1)
        offset = self.inst.query(f"C{channel}:OFST?")
        time.sleep(0.1)
        tdiv = self.inst.query(f"TDIV?")
        time.sleep(0.1)
        sara = self.inst.query(f"SARA?")
        time.sleep(0.1)
        
        

        sara_unit = {'G':1e9, 'M':1e6, 'k':1e3}
        for unit in sara_unit.keys():
            if sara.find(unit) != -1:
                sara = sara.split(unit)
                sara = float(sara[0]) * sara_unit[unit]
                break

        sara = float(sara)

        self.inst.write(f"C{channel}:WF? DAT2")
        time.sleep(0.1)
        raw = list(self.inst.read_raw())
        raw.pop()
        voltage = []
        time_value = []

        for data in raw:
            if data > 127:
                data = data - 255
            else:
                pass
            voltage.append(data)
        print(vdiv, offset, tdiv, sara)
        
        for n in range(0, len(voltage)):
            voltage[n] = voltage[n] / 25*float(vdiv)-float(offset)
            time_data = -(float(tdiv)*14/2)+n*(1/sara)
            time_value.append(time_data)

        
        return voltage, time_value
        
        




        
            

from . import utils
import time

class Waveform:
	"""
	Represents a waveform output channel of a signal generator.

	Parameters
	----------
	parent : object
		The parent instrument controller object.
	channel : int, optional
		Channel number on the instrument (default is 1).
	"""

	def __init__(self, parent, channel: int = 1):
		self.channel = channel
		self._parent = parent

	def sine(self, frequency: float, amplitude: float = 1.0, offset: float = 0.0,
			 phase: float = 0.0, high_level: float = None, low_level: float = None):
		"""
		Set a sine waveform.

		Parameters
		----------
		frequency : float
			Frequency in Hz.
		amplitude : float, optional
			Amplitude in Vpp (default is 1.0).
		offset : float, optional
			Offset voltage (default is 0.0).
		phase : float, optional
			Phase in degrees (default is 0.0).
		high_level : float, optional
			High voltage level.
		low_level : float, optional
			Low voltage level.
		"""
		
		if frequency > 120_000_000 or frequency < 1e-6:
			raise ValueError("Frequency must be between 1uHz and 120MHz.")
		
		utils.waveform(self._parent, frequency=frequency, amplitude=amplitude,
					   offset=offset, channel=self.channel, phase=phase,
					   wave_type="SINE", high_level=high_level, low_level=low_level)
		
        

	def square(self, frequency: float, amplitude: float = 1.0, offset: float = 0.0,
			   duty_cycle: float = 50.0, phase: float = 0.0,
			   high_level: float = None, low_level: float = None):
		"""
		Set a square waveform.

		Parameters
		----------
		frequency : float
		amplitude : float, optional
		offset : float, optional
		duty_cycle : float, optional
		phase : float, optional
		high_level : float, optional
		low_level : float, optional
		"""

		if frequency > 25_000_000 or frequency < 1e-6:
			raise ValueError("Frequency must be between 1uHz and 25MHz.")
		
		utils.waveform(self._parent, frequency=frequency, amplitude=amplitude,
					   offset=offset, channel=self.channel, phase=phase,
					   wave_type="SQUARE", duty_cycle=duty_cycle,
					   high_level=high_level, low_level=low_level)
		
	def pulse(self, frequency: float, amplitude: float = 1.0, offset: float = 0.0,
		   	duty_cycle: float = 50.0, width: float = 1e-6, rise: float = 1e-6, fall: float = 1e-6, 
			delay: float = 0.0, phase: float = 0.0, high_level: float = None, low_level: float = None):
		"""
		Set a pulse waveform with specific timing parameters.

		Parameters
		----------
		frequency : float
			Output frequency in Hz (1 µHz to 25 MHz).
		amplitude : float, optional
			Signal amplitude in volts peak-to-peak (default is 1.0).
		offset : float, optional
			DC offset voltage (default is 0.0).
		duty_cycle : float, optional
			Duty cycle in percent (default is 50.0).
		width : float, optional
			Pulse width in seconds (default is 1e-6).
		rise : float, optional
			Rise time in seconds (default is 1e-6).
		fall : float, optional
			Fall time in seconds (default is 1e-6).
		delay : float, optional
			Delay before pulse start in seconds (default is 0.0).
		phase : float, optional
			Phase shift in degrees (default is 0.0).
		high_level : float, optional
			High output level.
		low_level : float, optional
			Low output level.

		Raises
		------
		ValueError
			If frequency is not within the allowed range.
		"""

		if frequency > 25_000_000 or frequency < 1e-6:
			raise ValueError("Frequency must be between 1uHz and 25MHz.")
		
		utils.waveform(self._parent, frequency=frequency, amplitude=amplitude,
					   offset=offset, channel=self.channel, phase=phase,
					   wave_type="PULSE", duty_cycle=duty_cycle, pulse_width=width,
					   pulse_rise=rise, pulse_fall=fall, pulse_delay=delay, high_level=high_level,
					   low_level=low_level)

		

	def ramp(self, frequency: float, amplitude: float = 1.0, offset: float = 0.0,
			 symmetry: float = 50.0, phase: float = 0.0,
			 high_level: float = None, low_level: float = None):
		"""
		Set a ramp waveform.

		Parameters
		----------
		frequency : float
		amplitude : float, optional
		offset : float, optional
		symmetry : float, optional
		phase : float, optional
		high_level : float, optional
		low_level : float, optional
		"""
		if frequency > 1_000_000 or frequency < 1e-6:
			raise ValueError("Frequency must be between 1uHz and 1MHz.")
		
		utils.waveform(self._parent, frequency=frequency, amplitude=amplitude,
					   offset=offset, channel=self.channel, phase=phase,
					   wave_type="RAMP", symmetry=symmetry,
					   high_level=high_level, low_level=low_level)

	def triangle(self, frequency: float, amplitude: float = 1.0, offset: float = 0.0,
				 phase: float = 0.0, high_level: float = None, low_level: float = None):
		"""
		Set a triangle waveform.
		"""
		if frequency > 1_000_000 or frequency < 1e-6:
			raise ValueError("Frequency must be between 1uHz and 1MHz.")
		
		utils.waveform(self._parent, frequency=frequency, amplitude=amplitude,
					   offset=offset, channel=self.channel, phase=phase,
					   wave_type="RAMP", symmetry=50,
					   high_level=high_level, low_level=low_level)

	def sawtooth(self, frequency: float, amplitude: float = 1.0, offset: float = 0.0,
				 phase: float = 0.0, high_level: float = None, low_level: float = None):
		"""
		Set a sawtooth waveform.
		"""
		if frequency > 1_000_000 or frequency < 1e-6:
			raise ValueError("Frequency must be between 1uHz and 1MHz.")
		
		utils.waveform(self._parent, frequency=frequency, amplitude=amplitude,
					   offset=offset, channel=self.channel, phase=phase,
					   wave_type="RAMP", symmetry=0,
					   high_level=high_level, low_level=low_level)

	def on(self):
		"""
		Enable output on this channel.
		"""
		self._parent.inst.write(f"C{self.channel}:OUTP ON")

	def off(self):
		"""
		Disable output on this channel.
		"""
		self._parent.inst.write(f"C{self.channel}:OUTP OFF")

	def modulation(self, type: str = "AM", source: str = "INT", frequency: float = 1000.0,
				   depth: float = 50.0, waveform: str = "SINE",
				   deviation: float = 0, hop_frequency: float = None):
		"""
		Configure modulation settings.

		Parameters
		----------
		type : str
			Modulation type (AM, FM, PM, etc.).
		source : str
			Source signal (internal or external).
		frequency : float
		depth : float
		waveform : str
		deviation : float
		hop_frequency : float, optional
		"""
		if type not in ["AM", "FM", "PM", "FSK", "ASK", "PSK", "DSBAM", "PWM"]:
			raise ValueError("Invalid modulation type. Choose from AM, FM, PM, FSK, ASK, PSK, DSBAM, PWM.")

		if source not in ["INT", "EXT"]:
			raise ValueError("Invalid modulation source. Choose from internal or external.")

		if waveform not in ["SINE", "SQUARE", "TRIANGLE", "UPRAMP", "DNRAMP", "NOISE", "ARB"]:
			raise ValueError("Invalid waveform type.")

		if hop_frequency is None:
			hop_frequency = frequency
		
		time.sleep(0.1)
		if type == "AM":
			self._parent.inst.write(
				f"C{self.channel}:MDWV {type},MDSP,{waveform},STATE,ON,FRQ,{frequency},DEPTH,{depth},SRC,{source}")
		if type == "FM":
			self._parent.inst.write(
				f"C{self.channel}:MDWV {type},STATE,ON,MDSP,{waveform},FRQ,{frequency},DEVI,{deviation},SRC,{source}")
		if type == "PM":
			self._parent.inst.write(
				f"C{self.channel}:MDWV {type},STATE,ON,MDSP,{waveform},FRQ,{frequency},DEVI,{deviation},SRC,{source}")
		if type == "PWM":
			self._parent.inst.write(
				f"C{self.channel}:MDWV {type},STATE,ON,MDSP,{waveform},FRQ,{frequency},DEVI,{deviation},SRC,{source}")
		if type == "ASK":
			self._parent.inst.write(
				f"C{self.channel}:MDWV {type},STATE,ON,KFRQ,{frequency},SRC,{source}")
		if type == "FSK":
			self._parent.inst.write(
				f"C{self.channel}:MDWV {type},STATE,ON,KFRQ,{frequency},HRFQ,{hop_frequency},SRC,{source}")
		if type == "PSK":
			self._parent.inst.write(
				f"C{self.channel}:MDWV {type},STATE,ON,KFRQ,{frequency},SRC,{source}")
		

	def modulation_on(self):
		"""
		Turn modulation on.
		"""
		self._parent.inst.write(f"C{self.channel}:MDWV STATE,ON")

	def modulation_off(self):
		"""
		Turn modulation off.
		"""
		self._parent.inst.write(f"C{self.channel}:MDWV STATE,OFF")

	def sweep(self, sweep_time: float = 2, start_freq: float = 1000, stop_freq: float = 10000,
			  mode: str = "LINE", direction: str = "UP", trig_source: str = "INT"):
		"""
		Configure frequency sweep.

		Parameters
		----------
		sweep_time : float
		start_freq : float
		stop_freq : float
		mode : str
		direction : str
		trig_source : str
		"""
		if mode not in ["LINE", "LOG"]:
			raise ValueError("Invalid sweep mode")
		if direction not in ["UP", "DOWN"]:
			raise ValueError("Invalid sweep direction")
		if trig_source not in ["INT", "EXT"]:
			raise ValueError("Invalid trigger source")

		self._parent.inst.write(
			f"C{self.channel}:SWWV STATE,ON,TIME,{sweep_time},START,{start_freq},STOP,{stop_freq},"
			f"SWMD,{mode},DIR,{direction},TRSR,{trig_source}")

	def sweep_on(self):
		"""
		Enable frequency sweep.
		"""
		self._parent.inst.write(f"C{self.channel}:SWWV STATE,ON")

	def sweep_off(self):
		"""
		Disable frequency sweep.
		"""
		self._parent.inst.write(f"C{self.channel}:SWWV STATE,OFF")

	def burst(self, period: float = 1, start_phase: float = 0, mode: str = "NCYC",
			  trig_source: str = "INT", cycles: int = 1):
		"""
		Configure burst mode.

		Parameters
		----------
		period : float
		start_phase : float
		mode : str
		trig_source : str
		cycles : int
		"""
		self._parent.inst.write(
			f"C{self.channel}:BTWV STATE,ON,PRD,{period},STPS,{start_phase},GATE_NCYC,{mode},"
			f"TRSR,{trig_source},TIME,{cycles}")

	def burst_on(self):
		"""
		Enable burst mode.
		"""
		self._parent.inst.write(f"C{self.channel}:BTWV STATE,ON")

	def burst_off(self):
		"""
		Disable burst mode.
		"""
		self._parent.inst.write(f"C{self.channel}:BTWV STATE,OFF")

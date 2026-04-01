# EE-python

Clean instrument-control code for electrical measurements.

## Active Part of This Repo

- [source](/C:/Users/dinod/Desktop/EE%20python/EE-python/source) contains the reusable Python code.
- [examples](/C:/Users/dinod/Desktop/EE%20python/EE-python/examples) contains runnable usage examples grouped by instrument or use case.
- [scripts](/C:/Users/dinod/Desktop/EE%20python/EE-python/scripts) contains useful standalone bench utilities and instrument test scripts.
- [source/instruments](/C:/Users/dinod/Desktop/EE%20python/EE-python/source/instruments) contains the active instrument APIs.
- [archive](/C:/Users/dinod/Desktop/EE%20python/EE-python/archive) contains older material moved aside so the active repo stays readable.

## Design Direction

The active instrument APIs are built around a small common shape:

- `ping()`: report the current instrument situation as clearly as the hardware allows.
- `get()`: read one current parameter value from the instrument.
- `configure()`: change instrument state through one readable entry point.
- `measure()`: when an instrument supports it, return structured measurement data.

This keeps usage simple at the bench:

```python
from instruments import HP4192A

meter = HP4192A.open("TCPIP0::192.168.1.50::gpib0,17::INSTR")
meter.ping()
frequency_hz = meter.get("frequency_hz")
meter.configure(frequency_hz=1_000)
meter.close()
```

Each instrument should also have its own readable command reference so you do
not have to reopen the vendor manual to remember the command syntax.

## Current Focus

- First clean implementation: HP 4192A LF Impedance Analyzer
- Current goal inside that driver: expand readback, configuration, and measurement support
- Later: rewrite the existing Siglent APIs to match the same style

Useful files for the current HP 4192A work:

- [source/instruments/hp_4192a.py](/C:/Users/dinod/Desktop/EE%20python/EE-python/source/instruments/hp_4192a.py)
- [source/instruments/hp_4192a_commands.md](/C:/Users/dinod/Desktop/EE%20python/EE-python/source/instruments/hp_4192a_commands.md)
- [examples/hp_4192a/hp_4192a_user_guide.ipynb](/C:/Users/dinod/Desktop/EE%20python/EE-python/examples/hp_4192a/hp_4192a_user_guide.ipynb)
- [scripts/hp_4192a_test_scripts/configure_test.py](/C:/Users/dinod/Desktop/EE%20python/EE-python/scripts/hp_4192a_test_scripts/configure_test.py)
- [scripts/hp_4192a_test_scripts/measurement_test.py](/C:/Users/dinod/Desktop/EE%20python/EE-python/scripts/hp_4192a_test_scripts/measurement_test.py)
- [scripts/hp_4192a_test_scripts/get_test.py](/C:/Users/dinod/Desktop/EE%20python/EE-python/scripts/hp_4192a_test_scripts/get_test.py)
- [scripts/hp_4192a_test_scripts/self_test.py](/C:/Users/dinod/Desktop/EE%20python/EE-python/scripts/hp_4192a_test_scripts/self_test.py)
- [scripts/scan_keysight_gateway_gpib.py](/C:/Users/dinod/Desktop/EE%20python/EE-python/scripts/scan_keysight_gateway_gpib.py)

## Reference Manual

The HP 4192A implementation is being built from the local manual at:

`C:\Users\dinod\Desktop\HP manuals\HP 4192A OSM, fixtures OSM, App Note\4192A-OSM 474PGS.pdf`

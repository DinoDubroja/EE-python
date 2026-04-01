# Scripts

This folder contains useful bench and lab-utility scripts.

These scripts are different from `examples`:

- `examples` show how to use the library code
- `scripts` are standalone utilities that are useful to keep around

Current scope:

- gateway and bus scanning
- instrument test scripts
- other small lab helpers that do not belong inside the reusable API

Current layout:

- `scan_keysight_gateway_gpib.py`: safe scan of a Keysight gateway GPIB bus
- `hp_4192a_test_scripts/`: manual and automatic HP 4192A test scripts

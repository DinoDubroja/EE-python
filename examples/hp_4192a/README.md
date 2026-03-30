# HP 4192A Examples

This folder contains runnable HP 4192A example scripts.

- `configure_test.py`: step through all currently supported HP 4192A
  `configure()` features and pause after each `ping()` so you can compare with
  the front panel
- `measurement_test.py`: step through the current `measure()` behavior and
  compare returned data with the front panel and DUT setup
- `read_measurement.py`: call `measure()` once and print the returned
  measurement object in a readable form

Run examples from the repo root, for example:

```powershell
python examples/hp_4192a/configure_test.py
```

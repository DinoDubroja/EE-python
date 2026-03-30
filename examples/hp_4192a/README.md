# HP 4192A Examples

This folder contains runnable HP 4192A example scripts.

- `configure_test.py`: step through all currently supported HP 4192A
  `configure()` features and pause after each `ping()` so you can compare with
  the front panel
- `measurement_test.py`: step through all currently supported `measure()`
  display modes and compare returned data with the front panel and DUT setup
- `get_test.py`: select one supported `get()` parameter and print its current
  instrument value
- `self_test.py`: automatic short self-test for `configure()`, `get()`,
  `ping()`, and an optional `measure()` block when a known DUT is connected
- `self_test_benchmark.py`: run the current `self_test` repeatedly and write
  one Excel workbook with pass/fail statistics and failure traces

Run examples from the repo root, for example:

```powershell
python examples/hp_4192a/configure_test.py
```

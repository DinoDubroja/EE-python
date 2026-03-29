# HP 4192A Examples

This folder contains runnable HP 4192A example scripts.

- `check_frequency.py`: open the instrument, print `ping()`, change spot
  frequency with `configure()`, then print `ping()` again
- `check_primary_settings.py`: step through the first group of important
  settings and pause after each `ping()` so you can compare with the front
  panel
- `diagnose_commands.py`: send small raw-command tests one by one and watch the
  front panel

Run examples from the repo root, for example:

```powershell
python examples/hp_4192a/check_frequency.py
```

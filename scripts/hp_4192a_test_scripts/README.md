# HP 4192A Test Scripts

This folder contains HP 4192A bench-check and confidence-check scripts.

Contents:

- `configure_test.py`: guided manual check of `configure()`
- `measurement_test.py`: guided manual check of `measure()`
- `get_test.py`: one-shot terminal helper for `get()`
- `self_test.py`: automatic confidence check for the current API
- `self_test_benchmark.py`: repeat `self_test.py` many times and write an Excel report

Use this folder when you want to test the instrument or the driver.

Use [examples/hp_4192a](/C:/Users/dinod/Desktop/EE%20python/EE-python/examples/hp_4192a) when you want user-oriented examples of how to use the API in code.

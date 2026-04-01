# Examples

This folder contains user-facing examples.

Purpose:

- show how to use the active instrument APIs in a clean, user-oriented way
- keep test and diagnostic scripts out of the example layer
- group examples by instrument or by clear use case

Rule:

- reusable library code goes in `source`
- user-oriented examples and notebooks go in `examples`
- test, diagnostic, and bench-check scripts go in `scripts`

Current layout:

- `hp_4192a/`: notebook examples for the HP 4192A

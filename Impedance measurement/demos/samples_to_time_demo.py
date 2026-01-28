"""
Demo: build a time axis for a generated sine wave.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from util import generate_sine_samples, samples_to_time


def main():
    amplitude = 1.0
    phase = 0.0
    frequency = 2.0
    sample_rate = 20.0
    n_samples = 10

    samples = generate_sine_samples(
        amplitude=amplitude,
        phase=phase,
        frequency=frequency,
        sample_rate=sample_rate,
        n_samples=n_samples,
    )
    times = samples_to_time(samples, sample_rate)

    for i, (t, value) in enumerate(zip(times, samples)):
        print(f"{i}: t={t} s, x={value}")


if __name__ == "__main__":
    main()

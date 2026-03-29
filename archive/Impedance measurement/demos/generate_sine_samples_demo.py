"""
Demo: generate and plot a sine wave.
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from util import generate_sine_samples


def main():
    amplitude = 1.0
    phase = 0.0
    frequency = 2.0
    sample_rate = 200.0
    n_samples = int(sample_rate / frequency)

    samples = generate_sine_samples(
        amplitude=amplitude,
        phase=phase,
        frequency=frequency,
        sample_rate=sample_rate,
        n_samples=n_samples,
    )

    samples_repeated = samples * 3

    for i, value in enumerate(samples_repeated):
        print(f"{i}: {value}")

    times = [i / sample_rate for i in range(len(samples_repeated))]
    plt.plot(times, samples_repeated, marker="o")
    plt.title("Sine Wave Samples")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

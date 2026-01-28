"""
Demo: compare FFT and least-squares amplitude/phase estimates.
"""

import math
import os
import sys


import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from signal_class import Signal
from util import amplitude_phase_fft, generate_sine_samples, samples_to_time


def _wrap_phase(angle):
    while angle <= -math.pi:
        angle += 2.0 * math.pi
    while angle > math.pi:
        angle -= 2.0 * math.pi
    return angle


def main():
    amplitude = 1.2
    phase = 0.5
    frequency = 59.4
    sample_rate = 10000.0
    N = 5.0  # number of periods to sample
    n_samples = int(N / frequency * sample_rate)

    samples = generate_sine_samples(
        amplitude=amplitude,
        phase=phase,
        frequency=frequency,
        sample_rate=sample_rate,
        n_samples=n_samples,
    )
    times = samples_to_time(samples, sample_rate)
    signal = Signal(times, samples)
    est_amp1, est_phase1 = amplitude_phase_fft(times, samples, frequency)
    est_amp2, est_phase2 = signal.amplitude_phase_leastsquare(frequency)

    expected_phase = _wrap_phase(phase - (math.pi / 2.0))
    print(f"Expected amplitude: {amplitude}, estimated: {est_amp1}")
    print(f"Expected phase (cos): {expected_phase} rad, estimated: {est_phase1} rad")

    # Plot original signal and model in the same figure
    model1 = [
        est_amp1 * math.cos(2.0 * math.pi * frequency * t + est_phase1)
        for t in times
    ]

    model2 = [
        est_amp2 * math.cos(2.0 * math.pi * frequency * t + est_phase2)
        for t in times
    ]

    plt.figure(figsize=(8, 4))
    plt.plot(times, samples, color="darkred", linewidth=1.5, label="Original", marker='o', markersize=4)
    plt.plot(times, model1, color="steelblue", linewidth=1.5, label="FFT model")
    plt.plot(times, model2, color="darkgreen", linewidth=1.5, label="Least Squares model")
    plt.title("FFT and Least Squares Amplitude/Phase Estimates")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

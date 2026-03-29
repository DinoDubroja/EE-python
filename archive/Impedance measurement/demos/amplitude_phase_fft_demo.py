"""
Demo: estimate amplitude and phase with FFT and plot the fitted cosine.
"""

import math
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
    frequency = 5.0
    sample_rate = 100.0
    n_samples = 202

    samples = generate_sine_samples(
        amplitude=amplitude,
        phase=phase,
        frequency=frequency,
        sample_rate=sample_rate,
        n_samples=n_samples,
    )
    times = samples_to_time(samples, sample_rate)
    est_amp, est_phase = amplitude_phase_fft(times, samples, frequency)
    expected_phase = _wrap_phase(phase - (math.pi / 2.0))
    print(f"Expected amplitude: {amplitude}, estimated: {est_amp}")
    print(f"Expected phase (cos): {expected_phase} rad, estimated: {est_phase} rad")

    # Plot original signal and model in the same figure
    model = [
        est_amp * math.cos(2.0 * math.pi * frequency * t + est_phase)
        for t in times
    ]
    plt.figure(figsize=(8, 4))
    plt.plot(times, samples, color="darkred", linewidth=1.5, label="Original")
    plt.plot(times, model, color="steelblue", linewidth=1.5, label="FFT model")
    plt.title("FFT Amplitude/Phase Estimate")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

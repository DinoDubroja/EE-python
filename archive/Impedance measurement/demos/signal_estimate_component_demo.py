"""
Demo: estimate cosine amplitude and phase from a sine-generated signal.
"""

import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from signal_class import Signal
from util import generate_sine_samples, samples_to_time


def _wrap_phase(angle):
    while angle <= -math.pi:
        angle += 2.0 * math.pi
    while angle > math.pi:
        angle -= 2.0 * math.pi
    return angle


def main():
    amplitude = 1.5
    phase = 0.4
    frequency = 3.0
    sample_rate = 60.0
    n_samples = 120

    samples = generate_sine_samples(
        amplitude=amplitude,
        phase=phase,
        frequency=frequency,
        sample_rate=sample_rate,
        n_samples=n_samples,
    )
    times = samples_to_time(samples, sample_rate)
    signal = Signal(times, samples)

    signal.plot()

    est_amp, est_phase = signal.amplitude_phase_leastsquare(frequency)
    expected_phase = _wrap_phase(phase - (math.pi / 2.0))
    print(f"Expected amplitude: {amplitude}, estimated: {est_amp}")
    print(f"Expected phase (cos): {expected_phase} rad, estimated: {est_phase} rad")


if __name__ == "__main__":
    main()

"""
Demo: plot a sine wave using the Signal class.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from signal_class import Signal
from util import generate_sine_samples, samples_to_time


def main():
    amplitude = 1.0
    phase = 0.2
    frequency = 2.0
    sample_rate = 40.0
    n_samples = 80

    samples = generate_sine_samples(
        amplitude=amplitude,
        phase=phase,
        frequency=frequency,
        sample_rate=sample_rate,
        n_samples=n_samples,
    )
    times = samples_to_time(samples, sample_rate)
    signal = Signal(times, samples)

    signal.plot(
        t_start=0.0,
        t_stop=times[-1],
        color="darkred",
        y_label="Amplitude",
        x_label="Time (s)",
        grid=1,
        marker=True,
        line_width=1.5,
        title="Sine Wave Samples",
    )


if __name__ == "__main__":
    main()

"""
Utility helpers for generating and manipulating sampled signals.
"""

import math


def generate_sine_samples(amplitude, phase, frequency, sample_rate, n_samples):
    """
    Return N samples of a sine wave: x(t) = A * sin(2*pi*f*t + phase).

    - amplitude: peak value
    - phase: radians
    - frequency: Hz
    - sample_rate: Hz
    - n_samples: number of points
    """
    if n_samples < 0:
        raise ValueError("n_samples must be non-negative")
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")

    two_pi_f = 2.0 * math.pi * frequency
    return [
        amplitude * math.sin(two_pi_f * (i / sample_rate) + phase)
        for i in range(n_samples)
    ]


def samples_to_time(samples, sample_rate):
    """
    Create a time axis (seconds) for a list of samples.
    """
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    return [i / sample_rate for i in range(len(samples))]


def combine_time_samples(samples, times):
    """
    Combine two lists into (sample, time) pairs.
    """
    if len(times) != len(samples):
        raise ValueError("times and samples must have the same length")
    return list(zip(samples, times))


def amplitude_phase_fft(times, samples, frequency):
    """
    Estimate amplitude and phase at a frequency using an FFT bin.

    The phase returned is for a cosine reference:
    x(t) = A * cos(2*pi*f*t + phase).
    """
    if frequency < 0:
        raise ValueError("frequency must be non-negative")
    if len(times) != len(samples):
        raise ValueError("times and samples must have the same length")
    n = len(samples)
    if n == 0:
        raise ValueError("samples must be non-empty")

    import numpy as np

    dt = times[1] - times[0] if n > 1 else 1.0
    fft_result = np.fft.fft(samples)
    freqs = np.fft.fftfreq(n, d=dt)

    target_idx = np.argmin(np.abs(freqs - frequency))
    fft_value = fft_result[target_idx]

    amplitude = (2.0 / n) * np.abs(fft_value)
    phase = np.angle(fft_value)
    return amplitude, phase

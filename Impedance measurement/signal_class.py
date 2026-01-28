"""
Signal class for paired time and sample data, with simple analysis and plotting.
"""

import math


class Signal:
    """
    Container for equal-length time and sample lists.
    """

    def __init__(self, times, samples):
        if len(times) != len(samples):
            raise ValueError("times and samples must have the same length")
        self.times = list(times)
        self.samples = list(samples)

    def __len__(self):
        return len(self.samples)

    def pairs(self):
        """
        Return a list of (time, sample) pairs.
        """
        return list(zip(self.times, self.samples))

    def amplitude_phase_leastsquare(self, frequency):
        """
        Fit a cosine at the given frequency (Hz) and return (amplitude, phase).

        The phase is for a cosine model: x(t) = A * cos(2*pi*f*t + phase).
        """
        if frequency < 0:
            raise ValueError("frequency must be non-negative")
        if len(self) == 0:
            raise ValueError("signal must be non-empty")

        w = 2.0 * math.pi * frequency
        ss = 0.0
        cc = 0.0
        sc = 0.0
        xs = 0.0
        xc = 0.0
        for t, x in self.pairs():
            s = math.sin(w * t)
            c = math.cos(w * t)
            ss += s * s
            cc += c * c
            sc += s * c
            xs += x * s
            xc += x * c

        det = ss * cc - sc * sc
        if det == 0.0:
            raise ValueError("degenerate time grid for this frequency")

        a = (xc * ss - xs * sc) / det
        b = (xs * cc - xc * sc) / det
        amplitude = math.hypot(a, b)
        phase = math.atan2(-b, a)
        return amplitude, phase

    def plot(
        self,
        t_start=0.0,
        t_stop=None,
        color="darkred",
        y_label="Amplitude",
        x_label="Time",
        grid=0,
        marker=True,
        line_width=1.5,
        title="Signal",
    ):
        """
        Plot the signal with basic styling controls.
        """
        if len(self) == 0:
            raise ValueError("signal must be non-empty")

        if t_stop is None:
            t_stop = self.times[-1]

        if t_start > t_stop:
            raise ValueError("t_start must be <= t_stop")

        # Fixed plot properties (edit here if needed)
        figure_size = (8, 4)
        marker_style = "o" if marker else None
        marker_size = 3.5
        alpha = 0.95

        xs = []
        ys = []
        for t, x in self.pairs():
            if t_start <= t <= t_stop:
                xs.append(t)
                ys.append(x)

        if not xs:
            raise ValueError("no samples in the requested time window")

        import matplotlib.pyplot as plt

        plt.figure(figsize=figure_size)
        plt.plot(
            xs,
            ys,
            color=color,
            linewidth=line_width,
            marker=marker_style,
            markersize=marker_size,
            alpha=alpha,
        )
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if grid:
            plt.grid(True)
        plt.tight_layout()
        plt.show()

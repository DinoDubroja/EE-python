class WaveformParser:
    def __init__(self, preamble):
        # preamble fields: format, type, points, count, xIncrement, xOrigin, xRef, yIncrement, yOrigin, yRef
        _, _, self.n_points, _, self.x_incr, self.x_orig, self.x_ref, self.y_incr, self.y_orig, self.y_ref = map(float, preamble)

    def scale(self, raw_bytes):
        # convert raw ADC codes to voltage, and build time axis
        voltages = [ (b - self.y_ref)*self.y_incr + self.y_orig for b in raw_bytes ]
        times = [ self.x_orig + i*self.x_incr for i in range(len(voltages)) ]
        return times, voltages

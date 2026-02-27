# src/wrr/sediment.py

import numpy as np

class SedimentTransport:
    def __init__(self, slope, depth, grain_size):
        self.slope = slope
        self.depth = depth
        self.grain_size = grain_size

    def meyer_peter_muller(self):
        # Return zeros as placeholder transport values
        return np.zeros_like(self.slope)
# src/wrr/terrain.py

import numpy as np

def calculate_slope(elevation: np.ndarray, distance: np.ndarray) -> np.ndarray:
    """
    Placeholder slope calculation.

    Parameters
    ----------
    elevation : np.ndarray
        Elevation values along the channel
    distance : np.ndarray
        Distance along the channel

    Returns
    -------
    slope : np.ndarray
        Slope at each segment
    """
    print("Calculating slope (placeholder)")
    # simple finite difference
    slope = np.gradient(elevation, distance)
    return slope
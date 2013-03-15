import numpy as np

"""
Think of this as a "running" API: it contains useful methods for computing
various running statistics.
"""

def averagePace(distances, paces):
    """
    Computes the average pace.

    Parameters
    ----------
    distances : array, shape (N,)
        List of split distances (in miles).
    paces : array, shape (N,)
        List of times (in minutes) for each split.

    Returns
    -------
    avgpace : float
        The average overall pace.
    """
    return np.sum(paces) / np.sum(distances)

def metersToMiles(distances):
    """
    Converts splits in meters to miles.
    """
    return distances / 1609.0

def secondsToMinutes(times):
    """
    Converts splits in seconds to minutes.
    """
    return times / 60.0

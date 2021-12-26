"""Various utilities used by the library"""
import time
import warnings
from typing import List, Union

import numpy as np
import scipy.interpolate as interpolate


def format_time(value: float) -> str:
    """Convert time to nicer format"""
    if value <= 0.005:
        return f"{value * 1000000:.0f}us"
    elif value <= 0.1:
        return f"{value * 1000:.1f}ms"
    elif value > 86400:
        return f"{value / 86400:.2f}day"
    elif value > 1800:
        return f"{value / 3600:.2f}hr"
    elif value > 60:
        return f"{value / 60:.2f}min"
    return f"{value:.2f}s"


def time_loop(t_start: float, n_item: int, n_total: int, as_percentage: bool = True) -> str:
    """Calculate average, remaining and total times

    Parameters
    ----------
    t_start : float
        starting time of the for loop
    n_item : int
        index of the current item - assumes index starts at 0
    n_total : int
        total number of items in the for loop - assumes index starts at 0
    as_percentage : bool, optional
        if 'True', progress will be displayed as percentage rather than the raw value

    Returns
    -------
    timed : str
        loop timing information
    """
    t_tot = time.time() - t_start
    t_avg = t_tot / (n_item + 1)
    t_rem = t_avg * (n_total - n_item + 1)

    # calculate progress
    progress = f"{n_item}/{n_total + 1}"
    if as_percentage:
        progress = f"{(n_item / (n_total + 1)) * 100:.1f}%"

    return f"[Avg: {format_time(t_avg)} | Rem: {format_time(t_rem)} | Tot: {format_time(t_tot)} || {progress}]"


def shift(array, num, fill_value=0):
    """Shift 1d array to new position with 0 padding to prevent wraparound - this function is actually
    quicker than np.roll

    Parameters
    ----------
    array : np.ndarray
        array to be shifted
    num : int
        value by which the array should be shifted
    fill_value : Union[float, int]
        value to fill in the areas where wraparound would have happened
    """
    result = np.empty_like(array)
    if not isinstance(num, int):
        raise ValueError("`num` must be an integer")

    if num > 0:
        result[:num] = fill_value
        result[num:] = array[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = array[-num:]
    else:
        result[:] = array
    return result


def check_xy(x, array):
    """
    Check zvals input

    Parameters
    ----------
    x : np.ndarray
        1D array of separation units (N). The number of elements of xvals must equal the number of elements of
        zvals.shape[1]
    array : np.ndarray
        2D array of intensities that must have common separation units (M x N) where M is the number of vectors
        and N is number of points in the vector

    Returns
    -------
    zvals : np.ndarray
        2D array that should match the dimensions of xvals input
    """
    if x.shape[0] != array.shape[1]:
        if x.shape[0] != array.shape[0]:
            raise ValueError("Dimensions mismatch")
        array = array.T
        warnings.warn("The input array was rotated to match the x-axis input", UserWarning)

    return array


def generate_function(method, x, y):
    """
    Generate interpolation function

    Parameters
    ----------
    method : str
        name of the interpolator
    x : np.array
        1D array of separation units (N)
    y : np.ndarray
        1D array of intensity values (N)

    Returns
    -------
    fcn : scipy interpolator
        interpolation function
    """
    if method == "pchip":
        return interpolate.PchipInterpolator(x, y, extrapolate=False)
    return interpolate.interp1d(x, y, method, bounds_error=False, fill_value=0)


def find_nearest_index(x: np.ndarray, value: Union[float, int]):
    """Find index of nearest value

    Parameters
    ----------
    x : np.array
        input array
    value : number (float, int)
        input value
    Returns
    -------
    index : int
        index of nearest value
    """
    x = np.asarray(x)
    return np.argmin(np.abs(x - value))


def convert_peak_values_to_index(x: np.ndarray, peaks) -> List:
    """Converts non-integer peak values to index value by finding
    the nearest value in the `xvals` array.

    Parameters
    ----------
    x : np.array
        input array
    peaks : list
        list of peaks

    Returns
    -------
    peaks_idx : list
        list of peaks as index
    """
    return [find_nearest_index(x, peak) for peak in peaks]

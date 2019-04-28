"""Signal calibration and alignment by reference peaks - copy of MSALIGN function from MATLAB bioinformatics library."""
from __future__ import division
import numpy as np
import scipy.interpolate as interpolate

METHODS = ["pchip", "zero", "slinear", "quadratic", "cubic"]

__all__ = ["msalign"]


def msalign(xvals, zvals, peaks, **kwargs):
    """Signal calibration and alignment by reference peaks

    A simplified version of the MSALIGN function found in MATLAB (see references for link)

    This version of the msalign function accepts most of the parameters that MATLAB's function accepts with the
    following exceptions: GroupValue, ShowPlotValue. A number of other parameters is allowed, although they have been
    renamed to comply with PEP8 conventions. The Python version is 8-60 times slower than the MATLAB implementation,
    which is mostly caused by a really slow instantiation of the `scipy.interpolate.PchipInterpolator` interpolator. In
    order to speed things up, I've also included several other interpolation methods which are significantly faster
    and give similar results.

    References
    ----------
    Monchamp, P., Andrade-Cetto, L., Zhang, J.Y., and Henson, R. (2007) Signal Processing Methods for Mass
    Spectrometry. In Systems Bioinformatics: An Engineering Case-Based Approach, G. Alterovitz and M.F. Ramoni, eds.
    Artech House Publishers).
    MSALIGN: https://nl.mathworks.com/help/bioinfo/ref/msalign.html


    Parameters
    ----------
    xvals: numpy array
        1D array of separation units (N). The number of elements of xvals must equal the number of elements of
        zvals.shape[1]
    zvals: numpy array
        2D array of intensities that must have common separation units (M x N) where M is the number of vectors
        and N is number of points in the vector
    peaks: list
        list of reference peaks that must be found in the xvals vector
    method: str
        interpolation method. Default: 'cubic'. MATLAB version uses 'pchip' which is significantly slower in Python
    weights: list (optional)
        list of weights associated with the list of peaks. Must be the same length as list of peaks
    width: float (optional)
        width of the gaussian peak in separation units. Default: 10
    ratio: float (optional)
        scaling value that determines the size of the window around every alignment peak. The synthetic signal is
        compared to the input signal within these regions. Default: 2.5
    resolution: int (optional)
        Default: 100
    iterations: int (optional)
        number of iterations. Increasing this value will (slightly) slow down the function but will improve
        performance. Default: 5
    grid_steps: int (optional)
        number of steps to be used in the grid search. Default: 20
    shift_range: list / numpy array (optional)
        maximum allowed shifts. Default: [-100, 100]

    Returns
    -------
    zvals_out: numpy array
        calibrated array
    """
    n_signals = zvals.shape[0]

    # interpolation method
    method = kwargs.get("method", "cubic")
    # std dev of the Gaussian pulses (in X)
    gaussian_width = kwargs.get("width", 10)
    # sets the width of the windows use at every pulse
    gaussian_ratio = kwargs.get("ratio", 2.5)
    # resolution of every Gaussian pulse (number of points)
    gaussian_resolution = kwargs.get("resolution", 100)
    # increase to improve accuracy
    iterations = kwargs.get("iterations", 5)
    # size of grid for exhaustive search
    grid_steps = kwargs.get("grid_steps", 20)
    # initial shift range
    shift_range = kwargs.get("shift_range", np.array([-100, 100]))
    if isinstance(shift_range, list):
        shift_range = np.array(shift_range)

    # number of peaks
    P = peaks
    n_peaks = len(P)

    only_shift = False
    if n_peaks == 1:
        only_shift = True

    # weights
    W = kwargs.get("weights", np.ones(len(P)))

    if method not in METHODS:
        raise ValueError(
            "Method `{}` not found in the method options: {}".format(method, METHODS)
        )
    if len(W) != n_peaks:
        raise ValueError("Number of weights does not match number of peaks")
    if len(shift_range) != 2:
        raise ValueError(
            "Number of 'shift_values' is not correct. Shift range accepts"
            " numpy array with two values."
        )
    if np.diff(shift_range) == 0:
        raise ValueError("Values of 'shift_values' must not be the same!")
    if gaussian_ratio <= 0:
        raise ValueError("Value of 'ratio' must be above 0!")
    if iterations <= 0:
        raise ValueError("Value of 'iterations' must be above 0!")
    if grid_steps <= 0:
        raise ValueError("Value of 'grid_steps' must be above 0!")
    if gaussian_resolution <= 0:
        raise ValueError("Value of 'resolution' must be above 0!")

    # check that values for gaussian_width are valid
    G = np.zeros((n_peaks, 1))
    for i in range(n_peaks):
        G[i] = gaussian_width

    # set the synthetic target signal
    corr_sig_x = np.zeros((gaussian_resolution + 1, n_peaks))
    corr_sig_y = np.zeros((gaussian_resolution + 1, n_peaks))

    gaussian_resolution_range = np.arange(0, gaussian_resolution + 1)
    for i in range(n_peaks):
        leftL = P[i] - gaussian_ratio * G[i]
        rightL = P[i] + gaussian_ratio * G[i]
        corr_sig_x[:, i] = leftL + (
            gaussian_resolution_range * (rightL - leftL) / gaussian_resolution
        )
        corr_sig_y[:, i] = W[i] * np.exp(-np.square((corr_sig_x[:, i] - P[i]) / G[i]))

    corr_sig_l = (gaussian_resolution + 1) * n_peaks
    corr_sig_x = corr_sig_x.flatten("F")
    corr_sig_y = corr_sig_y.flatten("F")

    # set reduce_range_factor to take 5 points of the previous ranges or half of
    # the previous range if grid_steps<10
    reduce_range_factor = min(0.5, 5 / grid_steps)

    # set scl such that the maximum peak can shift no more than the
    # limits imposed by shft when scaling
    scale_range = 1 + shift_range / max(P)

    if only_shift:
        scale_range = np.array([1, 1])

    # allocate space for vectors of optima
    scale_opt = np.zeros((n_signals, 1))
    shift_opt = np.zeros((n_signals, 1))

    # create the meshgrid only once
    A, B = np.meshgrid(
        np.divide(np.arange(0, grid_steps), grid_steps - 1),
        np.divide(np.arange(0, grid_steps), grid_steps - 1),
    )
    search_space = np.tile(
        np.vstack([A.flatten(order="F"), B.flatten(order="F")]).T, [1, iterations]
    )

    # iterate for every signal
    for n_signal in range(n_signals):
        # Main loop: searches for optimum values for the Scale and Shift
        # factors by exhaustive search over a multiresolution grid, getting
        # finer at every iteration.

        # set to back to the user input arguments (or default)
        shft = shift_range
        scl = scale_range

        # generate the interpolation function early on to save time
        # the function instantiation is by far the slowest step, hence we want to
        # minimise the number of times this is performed
        if method == "pchip":
            f = interpolate.PchipInterpolator(xvals, zvals[n_signal])
        else:
            f = interpolate.interp1d(
                xvals, zvals[n_signal], method, bounds_error=False, fill_value=0
            )

        for n_iter in range(iterations):  # increase for better resolution
            # scale and shift search space
            A = scl[0] + search_space[:, n_iter * (2 - 1)] * np.diff(scl)
            B = shft[0] + search_space[:, (n_iter * 2) + 1] * np.diff(shft)
            temp = (
                np.reshape(A, (A.shape[0], 1))
                * np.reshape(corr_sig_x, (1, corr_sig_x.shape[0]))
                + np.tile(B, [corr_sig_l, 1]).T
            )
            temp = f(temp.flatten("C")).reshape((temp.shape))
            imax = np.dot(temp, corr_sig_y).argmax()

            # save optimum
            scale_opt[n_signal] = A[imax]
            shift_opt[n_signal] = B[imax]

            # readjust grid for next iteration
            scl = (
                scale_opt[n_signal]
                + np.array([-0.5, 0.5]) * np.diff(scl) * reduce_range_factor
            )
            shft = (
                shift_opt[n_signal]
                + np.array([-0.5, 0.5]) * np.diff(shft) * reduce_range_factor
            )

    zvals_out = np.zeros_like(zvals)
    for n_signal in range(n_signals):
        # interpolate back to the original domain
        if method == "pchip":
            zvals_out[n_signal] = interpolate.pchip_interpolate(
                (xvals - shift_opt[n_signal]) / scale_opt[n_signal],
                zvals[n_signal],
                xvals,
            )
        else:
            zvals_out[n_signal] = interpolate.interp1d(
                (xvals - shift_opt[n_signal]) / scale_opt[n_signal],
                zvals[n_signal],
                method,
                bounds_error=False,
                fill_value=0,
            )(xvals)

    return zvals_out


if __name__ == "__main__":
    from time import time as ttime

    # MATLAB test dataset
    peaks = [3991.4, 4598, 7964, 9160]
    kwargs = dict(
        iterations=5,
        weights=[60, 100, 60, 100],
        resolution=100,
        grid_steps=20,
        ratio=2.5,
        shift_range=[-100, 100],
    )

    fname = r"./example_data/msalign_test_data.csv"
    data = np.genfromtxt(fname, delimiter=",")
    xvals = data[1:, 0]
    yvals = data[0, 1:]
    zvals = data[1:, 1:].T

    for method in ["pchip", "zero", "slinear", "quadratic", "cubic"]:
        kwargs.update(dict(method=method))
        tstart = ttime()
        zvals_new = msalign(xvals, zvals, peaks, **kwargs)
        print(
            "File - {} :: Method - {} :: Time - {:.4f}".format(
                fname, method, ttime() - tstart
            )
        )
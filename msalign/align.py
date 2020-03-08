"""Main alignment class"""
# Standard library imports
import time
import logging
from typing import List

# Third-party imports
import numpy as np

# Local imports
from msalign.utilities import shift
from msalign.utilities import check_xy
from msalign.utilities import time_loop
from msalign.utilities import format_time
from msalign.utilities import generate_function
from msalign.utilities import convert_peak_values_to_index

METHODS = ["pchip", "zero", "slinear", "quadratic", "cubic", "linear"]
LOGGER = logging.getLogger(__name__)


class Aligner:
    def __init__(
        self,
        x: np.ndarray,
        array: np.ndarray,
        peaks: List,
        method: str = "cubic",
        width: int = 10,
        ratio: float = 2.5,
        resolution: int = 100,
        iterations: int = 5,
        grid_steps: int = 20,
        shift_range: List = None,
        weights: List = None,
        return_shifts: bool = False,
        align_by_index: bool = False,
        only_shift: bool = False,
        quick_shift: bool = False,
    ):
        """Signal calibration and alignment by reference peaks

        A simplified version of the MSALIGN function found in MATLAB (see references for link)

        This version of the msalign function accepts most of the parameters that MATLAB's function accepts with the
        following exceptions: GroupValue, ShowPlotValue. A number of other parameters is allowed, although they have
        been renamed to comply with PEP8 conventions. The Python version is 8-60 times slower than the MATLAB
        implementation, which is mostly caused by a really slow instantiation of the
        `scipy.interpolate.PchipInterpolator` interpolator. In order to speed things up, I've also included several
        other interpolation methods which are significantly faster and give similar results.

        References
        ----------
        Monchamp, P., Andrade-Cetto, L., Zhang, J.Y., and Henson, R. (2007) Signal Processing Methods for Mass
        Spectrometry. In Systems Bioinformatics: An Engineering Case-Based Approach, G. Alterovitz and M.F. Ramoni, eds.
        Artech House Publishers).
        MSALIGN: https://nl.mathworks.com/help/bioinfo/ref/msalign.html

        Parameters
        ----------
        x : np.ndarray
            1D array of separation units (N). The number of elements of xvals must equal the number of elements of
            zvals.shape[1]
        array : np.ndarray
            2D array of intensities that must have common separation units (M x N) where M is the number of vectors
            and N is number of points in the vector
        peaks : list
            list of reference peaks that must be found in the xvals vector
        method : str
            interpolation method. Default: 'cubic'. MATLAB version uses 'pchip' which is significantly slower in Python
        weights: list (optional)
            list of weights associated with the list of peaks. Must be the same length as list of peaks
        width : float (optional)
            width of the gaussian peak in separation units. Default: 10
        ratio : float (optional)
            scaling value that determines the size of the window around every alignment peak. The synthetic signal is
            compared to the input signal within these regions. Default: 2.5
        resolution : int (optional)
            Default: 100
        iterations : int (optional)
            number of iterations. Increasing this value will (slightly) slow down the function but will improve
            performance. Default: 5
        grid_steps : int (optional)
            number of steps to be used in the grid search. Default: 20
        shift_range : list / numpy array (optional)
            maximum allowed shifts. Default: [-100, 100]
        only_shift : bool
            determines if signal should be shifted (True) or rescaled (False). Default: True
        return_shifts : bool
            decide whether shift parameter `shift_opt` should also be returned. Default: False
        align_by_index : bool
            decide whether alignment should be done based on index rather than `xvals` array. Default: False

        Returns
        -------
        zvals_out : numpy array
            calibrated array
        shift_opt : numpy array (optional)
            amount of shift for each signal. Only returned if return_shift is set to True
        """
        t_start = time.time()
        # set input
        self.x = np.asarray(x)
        self.array = check_xy(self.x, np.asarray(array))
        self.peaks = list(peaks)

        # set attributes
        self.n_signals = self.array.shape[0]
        self.n_peaks = len(self.peaks)

        # accessible attributes
        self.array_aligned = np.zeros_like(self.array)
        self.scale_opt = np.ones((self.n_signals, 1), dtype=np.float32)
        self.shift_opt = np.zeros((self.n_signals, 1), dtype=np.float32)

        # interpolation method
        self._method = method
        # std dev of the Gaussian pulses (in X)
        self._gaussian_width = width
        # sets the width of the windows use at every pulse
        self._gaussian_ratio = ratio
        # resolution of every Gaussian pulse (number of points)
        self._gaussian_resolution = resolution
        # increase to improve accuracy
        self._n_iterations = iterations
        # size of grid for exhaustive search
        self._grid_steps = grid_steps
        # initial shift range
        if shift_range is None:
            shift_range = [-100, 100]
        self._shift_range = np.asarray(shift_range)
        # return shift vector
        self._return_shifts = return_shifts
        # align signals by index rather than peak value
        self._align_by_index = align_by_index
        # align by index - rather than aligning to arbitrary non-integer values in the xvals, you can instead
        # use index of those values
        if self._align_by_index:
            self.peaks = convert_peak_values_to_index(self.x, self.peaks)
            self.x = np.arange(self.x.shape[0])
            LOGGER.debug(f"Aligning by index - peak positions: {self.peaks}")
        self._only_shift = only_shift
        if self.n_peaks == 1:
            self._only_shift = True
        # weights
        if weights is None:
            weights = np.ones(self.n_peaks)
        self._weights = weights

        # enable quick realignment
        self._quick_shift = quick_shift

        # private attributes
        self._corr_sig_l = None
        self._corr_sig_x = None
        self._corr_sig_y = None
        self._reduce_range_factor = None
        self._scale_range = None
        self._search_space = None

        # validate inputs
        self.validate()

        # prepare
        self.prepare()
        LOGGER.debug(f"Initialized in {format_time(time.time()-t_start)}")

    def validate(self):
        """Ensures the user-set parameters are correct"""
        # check user-specified parameters
        if self._method not in METHODS:
            raise ValueError("Method `{}` not found in the method options: {}".format(self._method, METHODS))
        if not isinstance(self._weights, (list, set, np.ndarray)) or len(self._weights) != self.n_peaks:
            raise ValueError("Number of weights does not match number of peaks")
        if len(self._shift_range) != 2:
            raise ValueError(
                "Number of 'shift_values' is not correct. Shift range accepts" " numpy array with two values."
            )
        if np.diff(self._shift_range) == 0:
            raise ValueError("Values of 'shift_values' must not be the same!")
        if self._gaussian_ratio <= 0:
            raise ValueError("Value of 'ratio' must be above 0!")
        if self._n_iterations <= 0 or isinstance(self._n_iterations, float):
            raise ValueError("Value of 'iterations' must be above 0 and be an integer!")
        if self._grid_steps <= 0:
            raise ValueError("Value of 'grid_steps' must be above 0!")
        if self._gaussian_resolution <= 0:
            raise ValueError("Value of 'resolution' must be above 0!")
        if not isinstance(self._only_shift, bool):
            raise ValueError("Value of 'only_shift' must be a boolean")
        if not isinstance(self._return_shifts, bool):
            raise ValueError("Value of 'return_shift' must be a boolean")
        if not isinstance(self._align_by_index, bool):
            raise ValueError("Value of 'align_by_index' must be a boolean")
        if self._quick_shift and not self._only_shift:
            raise ValueError(
                "Cannot set `quick_shift` with rescaling since quick shift is accomplished by simply"
                " moving spectra along the axis without interpolation"
            )
        if self._quick_shift and not self._align_by_index:
            raise ValueError(
                "Cannot set `quick_shift` without also setting the `align_by_index` to `True`. Quick shift"
                " simply moves the spectra without interpolation so it relies on moving values by their"
                " index which is not calculated correctly when using `true` x-axis values."
            )

    def prepare(self):
        """Prepare dataset for alignment"""
        t_start = time.time()
        # check that values for gaussian_width are valid
        gaussian_widths = np.zeros((self.n_peaks, 1))
        for i in range(self.n_peaks):
            gaussian_widths[i] = self._gaussian_width

        # set the synthetic target signal
        corr_sig_x = np.zeros((self._gaussian_resolution + 1, self.n_peaks))
        corr_sig_y = np.zeros((self._gaussian_resolution + 1, self.n_peaks))

        gaussian_resolution_range = np.arange(0, self._gaussian_resolution + 1)
        for i in range(self.n_peaks):
            left_l = self.peaks[i] - self._gaussian_ratio * gaussian_widths[i]
            right_l = self.peaks[i] + self._gaussian_ratio * gaussian_widths[i]
            corr_sig_x[:, i] = left_l + (gaussian_resolution_range * (right_l - left_l) / self._gaussian_resolution)
            corr_sig_y[:, i] = self._weights[i] * np.exp(
                -np.square((corr_sig_x[:, i] - self.peaks[i]) / gaussian_widths[i])
            )

        self._corr_sig_l = (self._gaussian_resolution + 1) * self.n_peaks
        self._corr_sig_x = corr_sig_x.flatten("F")
        self._corr_sig_y = corr_sig_y.flatten("F")

        # set reduce_range_factor to take 5 points of the previous ranges or half of
        # the previous range if grid_steps < 10
        self._reduce_range_factor = min(0.5, 5 / self._grid_steps)

        # set scl such that the maximum peak can shift no more than the limits imposed by shft when scaling
        self._scale_range = 1 + self._shift_range / max(self.peaks)

        if self._only_shift:
            self._scale_range = np.array([1, 1])

        # create the meshgrid only once
        mesh_a, mesh_b = np.meshgrid(
            np.divide(np.arange(0, self._grid_steps), self._grid_steps - 1),
            np.divide(np.arange(0, self._grid_steps), self._grid_steps - 1),
        )
        self._search_space = np.tile(
            np.vstack([mesh_a.flatten(order="F"), mesh_b.flatten(order="F")]).T, [1, self._n_iterations]
        )
        LOGGER.debug(f"Prepared in {format_time(time.time() - t_start)}")

    def run(self):
        """Execute the alignment procedure for each signal in the 2D array and collate the shift/scale vectors"""
        # iterate for every signal
        t_start = time.time()

        _scale_range = np.array([-0.5, 0.5])
        for n_signal, y in enumerate(self.array):

            # main loop: searches for the optimum values of Scale and Shift factors by search over a multi-resolution
            # grid, getting better at each iteration. Increasing the number of iterations improves the shift and scale
            # parameters

            # set to back to the user input arguments (or default)
            _shift = self._shift_range
            _scale = self._scale_range

            # generate interpolation function for each signal - instantiation of the interpolator can be quite slow,
            # so you can slightly increase the number of iterations without significant slowdown of the process
            fcn = generate_function(self._method, self.x, y)

            # iterate to estimate the shift and scale - at each iteration, the grid search is readjusted and the
            # shift/scale values are optimized further
            for n_iter in range(self._n_iterations):
                # scale and shift search space
                scale_grid = _scale[0] + self._search_space[:, (n_iter * 2) - 2] * np.diff(_scale)
                shift_grid = _shift[0] + self._search_space[:, (n_iter * 2) + 1] * np.diff(_shift)
                temp = (
                    np.reshape(scale_grid, (scale_grid.shape[0], 1))
                    * np.reshape(self._corr_sig_x, (1, self._corr_sig_l))
                    + np.tile(shift_grid, [self._corr_sig_l, 1]).T
                )
                # interpolate at each iteration. Need to remove NaNs which can be introduced by certain (e.g.
                # PCHIP) interpolator
                temp = np.nan_to_num(fcn(temp.flatten("C")).reshape(temp.shape))

                # determine the best position
                i_max = np.dot(temp, self._corr_sig_y).argmax()

                # save optimum value
                self.scale_opt[n_signal] = scale_grid[i_max]
                self.shift_opt[n_signal] = shift_grid[i_max]

                # readjust grid for next iteration_reduce_range_factor
                _scale = self.scale_opt[n_signal] + _scale_range * np.diff(_scale) * self._reduce_range_factor
                _shift = self.shift_opt[n_signal] + _scale_range * np.diff(_shift) * self._reduce_range_factor
        msg = f"Processed {self.n_signals} signals " + time_loop(t_start, self.n_signals + 1, self.n_signals)
        LOGGER.info(msg)

        # re-align arrays
        if self._quick_shift:
            self.shift()
        else:
            self.realign()

        # return aligned data and shifts
        if self._return_shifts:
            return self.array_aligned, self.shift_opt

        # only return data
        return self.array_aligned

    def realign(self, shift_opt=None, scale_opt=None):
        """Realign array based on the optimized shift and scale parameters

        Parameters
        ----------
        shift_opt: Optional[np.ndarray]
            vector containing values by which to shift the array
        scale_opt : Optional[np.ndarray]
            vector containing values by which to rescale the array
        """
        t_start = time.time()
        if shift_opt is None:
            shift_opt = self.shift_opt
        if scale_opt is None:
            scale_opt = self.scale_opt

        # realign based on provided values
        for iteration, y in enumerate(self.array):
            # interpolate back to the original domain
            fcn = generate_function(self._method, (self.x - shift_opt[iteration]) / scale_opt[iteration], y)
            self.array_aligned[iteration] = np.nan_to_num(fcn(self.x))

        msg = f"Re-aligned {self.n_signals} signals " + time_loop(t_start, self.n_signals + 1, self.n_signals)
        LOGGER.info(msg)

    def shift(self, shift_opt=None):
        """Quickly shift array based on the optimized shift parameters

        Parameters
        ----------
        shift_opt: Optional[np.ndarray]
            vector containing values by which to shift the array
        """
        t_start = time.time()
        if shift_opt is None:
            shift_opt = np.round(self.shift_opt, 0).astype(np.int32)

        # quickly shift based on provided values
        for iteration, y in enumerate(self.array):
            self.array_aligned[iteration] = shift(y, -int(shift_opt[iteration]))

        msg = f"Re-aligned {self.n_signals} signals " + time_loop(t_start, self.n_signals + 1, self.n_signals)
        print(msg)
        LOGGER.debug(msg)

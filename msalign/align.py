"""Main alignment class"""
import logging
import time
import typing as ty
import warnings

import numpy as np

from .utilities import check_xy, convert_peak_values_to_index, generate_function, shift, time_loop

METHODS = ["pchip", "zero", "slinear", "quadratic", "cubic", "linear"]
LOGGER = logging.getLogger(__name__)


class Aligner:
    """Main alignment class"""

    _method, _gaussian_ratio, _gaussian_resolution, _gaussian_width, _n_iterations = None, None, None, None, None
    _corr_sig_l, _corr_sig_x, _corr_sig_y, _reduce_range_factor, _scale_range = None, None, None, None, None
    _search_space, _computed = None, False

    def __init__(
        self,
        x: np.ndarray,
        array: ty.Optional[np.ndarray],
        peaks: ty.Iterable[float],
        method: str = "cubic",
        width: float = 10,
        ratio: float = 2.5,
        resolution: int = 100,
        iterations: int = 5,
        grid_steps: int = 20,
        shift_range: ty.Optional[ty.Tuple[int, int]] = None,
        weights: ty.Optional[ty.List[float]] = None,
        return_shifts: bool = False,
        align_by_index: bool = False,
        only_shift: bool = False,
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
        """
        self.x = np.asarray(x)
        if array is not None:
            self.array = check_xy(self.x, np.asarray(array))
        else:
            self.array = np.empty((0, len(self.x)))

        self.n_signals = self.array.shape[0]
        self.array_aligned = np.zeros_like(self.array)
        self.peaks = list(peaks)

        # set attributes
        self.n_peaks = len(self.peaks)

        # accessible attributes
        self.scale_opt = np.ones((self.n_signals, 1), dtype=np.float32)
        self.shift_opt = np.zeros((self.n_signals, 1), dtype=np.float32)
        self.shift_values = np.zeros_like(self.shift_opt)

        self.method = method
        self.gaussian_ratio = ratio
        self.gaussian_resolution = resolution
        self.gaussian_width = width
        self.n_iterations = iterations
        self.grid_steps = grid_steps
        if shift_range is None:
            shift_range = [-100, 100]
        self.shift_range = shift_range
        if weights is None:
            weights = np.ones(self.n_peaks)
        self.weights = weights

        # return shift vector
        self._return_shifts = return_shifts
        # If the number of points is equal to 1, then only shift
        if self.n_peaks == 1:
            only_shift = True
        if only_shift and not align_by_index:
            align_by_index = True
            LOGGER.warning("Only computing shifts - changed `align_by_index` to `True`.")

        # align signals by index rather than peak value
        self._align_by_index = align_by_index
        # align by index - rather than aligning to arbitrary non-integer values in the xvals, you can instead
        # use index of those values
        if self._align_by_index:
            self.peaks = convert_peak_values_to_index(self.x, self.peaks)
            self.x = np.arange(self.x.shape[0])
            LOGGER.debug(f"Aligning by index - peak positions: {self.peaks}")
        self._only_shift = only_shift

        self._initialize()

    @property
    def method(self):
        """Interpolation method."""
        return self._method

    @method.setter
    def method(self, value: str):
        if value not in METHODS:
            raise ValueError(f"Method `{value}` not found in the method options: {METHODS}")
        self._method = value

    @property
    def gaussian_ratio(self):
        """Gaussian ratio."""
        return self._gaussian_ratio

    @gaussian_ratio.setter
    def gaussian_ratio(self, value: float):
        if value <= 0:
            raise ValueError("Value of 'ratio' must be above 0!")
        self._gaussian_ratio = value

    @property
    def gaussian_resolution(self):
        """Gaussian resolution of every Gaussian pulse (number of points)."""
        return self._gaussian_resolution

    @gaussian_resolution.setter
    def gaussian_resolution(self, value: float):
        if value <= 0:
            raise ValueError("Value of 'resolution' must be above 0!")
        self._gaussian_resolution = value

    @property
    def gaussian_width(self):
        """Width of the Gaussian pulse in std dev of the Gaussian pulses (in X)."""
        return self._gaussian_width

    @gaussian_width.setter
    def gaussian_width(self, value: float):
        self._gaussian_width = value

    @property
    def n_iterations(self):
        """Total number of iterations - increase to improve accuracy."""
        return self._n_iterations

    @n_iterations.setter
    def n_iterations(self, value: int):
        if value < 1 or not isinstance(value, int):
            raise ValueError("Value of 'iterations' must be above 0 and be an integer!")
        self._n_iterations = value

    @property
    def grid_steps(self):
        """Total number of iterations - increase to improve accuracy."""
        return self._grid_steps

    @grid_steps.setter
    def grid_steps(self, value: int):
        if value < 1 or not isinstance(value, int):
            raise ValueError("Value of 'iterations' must be above 0 and be an integer!")
        self._grid_steps = value

    @property
    def shift_range(self):
        """Total number of iterations - increase to improve accuracy."""
        return self._shift_range

    @shift_range.setter
    def shift_range(self, value: ty.Tuple[float, float]):
        if len(value) != 2:
            raise ValueError(
                "Number of 'shift_values' is not correct. Shift range accepts" " numpy array with two values."
            )
        if np.diff(value) == 0:
            raise ValueError("Values of 'shift_values' must not be the same!")
        self._shift_range = np.asarray(value)

    @property
    def weights(self):
        """Total number of iterations - increase to improve accuracy."""
        return self._weights

    @weights.setter
    def weights(self, value: ty.Optional[ty.Iterable[float]]):
        if value is None:
            value = np.ones(self.n_peaks)
        if not isinstance(value, ty.Iterable):
            raise ValueError("Weights must be provided as an iterable.")
        if len(value) != self.n_peaks:
            raise ValueError("Number of weights does not match the number of peaks.")
        self._weights = np.asarray(value)

    def _initialize(self):
        """Prepare dataset for alignment"""
        # check that values for gaussian_width are valid
        gaussian_widths = np.zeros((self.n_peaks, 1))
        for i in range(self.n_peaks):
            gaussian_widths[i] = self.gaussian_width

        # set the synthetic target signal
        corr_sig_x = np.zeros((self.gaussian_resolution + 1, self.n_peaks))
        corr_sig_y = np.zeros((self.gaussian_resolution + 1, self.n_peaks))

        gaussian_resolution_range = np.arange(0, self.gaussian_resolution + 1)
        for i in range(self.n_peaks):
            left_l = self.peaks[i] - self.gaussian_ratio * gaussian_widths[i]  # noqa
            right_l = self.peaks[i] + self.gaussian_ratio * gaussian_widths[i]  # noqa
            corr_sig_x[:, i] = left_l + (gaussian_resolution_range * (right_l - left_l) / self.gaussian_resolution)
            corr_sig_y[:, i] = self.weights[i] * np.exp(
                -np.square((corr_sig_x[:, i] - self.peaks[i]) / gaussian_widths[i])  # noqa
            )

        self._corr_sig_l = (self.gaussian_resolution + 1) * self.n_peaks
        self._corr_sig_x = corr_sig_x.flatten("F")
        self._corr_sig_y = corr_sig_y.flatten("F")

        # set reduce_range_factor to take 5 points of the previous ranges or half of
        # the previous range if grid_steps < 10
        self._reduce_range_factor = min(0.5, 5 / self.grid_steps)

        # set scl such that the maximum peak can shift no more than the limits imposed by shift when scaling
        self._scale_range = 1 + self.shift_range / max(self.peaks)

        if self._only_shift:
            self._scale_range = np.array([1, 1])

        # create the mesh-grid only once
        mesh_a, mesh_b = np.meshgrid(
            np.divide(np.arange(0, self.grid_steps), self.grid_steps - 1),
            np.divide(np.arange(0, self.grid_steps), self.grid_steps - 1),
        )
        self._search_space = np.tile(
            np.vstack([mesh_a.flatten(order="F"), mesh_b.flatten(order="F")]).T, [1, self._n_iterations]
        )

    def run(self, n_iterations: int = None):
        """Execute the alignment procedure for each signal in the 2D array and collate the shift/scale vectors"""
        self.n_iterations = n_iterations or self.n_iterations
        # iterate for every signal
        t_start = time.time()

        # main loop: searches for the optimum values of Scale and Shift factors by search over a multi-resolution
        # grid, getting better at each iteration. Increasing the number of iterations improves the shift and scale
        # parameters
        for n_signal, y in enumerate(self.array):
            self.shift_opt[n_signal], self.scale_opt[n_signal] = self.compute(y)
        LOGGER.debug(f"Processed {self.n_signals} signals " + time_loop(t_start, self.n_signals + 1, self.n_signals))
        self._computed = True

    def compute(self, y: np.ndarray) -> ty.Tuple[float, float]:
        """Compute correction factors.

        This function does not set value in any of the class attributes so can be used in a iterator where values
        are computed lazily.
        """
        _scale_range = np.array([-0.5, 0.5])
        scale_opt, shift_opt = 0.0, 1.0

        # set to back to the user input arguments (or default)
        _shift = self.shift_range.copy()
        _scale = self._scale_range.copy()

        # generate interpolation function for each signal - instantiation of the interpolator can be quite slow,
        # so you can slightly increase the number of iterations without significant slowdown of the process
        func = generate_function(self.method, self.x, y)

        # iterate to estimate the shift and scale - at each iteration, the grid search is readjusted and the
        # shift/scale values are optimized further
        for n_iter in range(self.n_iterations):
            # scale and shift search space
            scale_grid = _scale[0] + self._search_space[:, (n_iter * 2) - 2] * np.diff(_scale)
            shift_grid = _shift[0] + self._search_space[:, (n_iter * 2) + 1] * np.diff(_shift)
            temp = (
                np.reshape(scale_grid, (scale_grid.shape[0], 1)) * np.reshape(self._corr_sig_x, (1, self._corr_sig_l))
                + np.tile(shift_grid, [self._corr_sig_l, 1]).T
            )
            # interpolate at each iteration. Need to remove NaNs which can be introduced by certain (e.g.
            # PCHIP) interpolator
            temp = np.nan_to_num(func(temp.flatten("C")).reshape(temp.shape))

            # determine the best position
            i_max = np.dot(temp, self._corr_sig_y).argmax()

            # save optimum value
            scale_opt = scale_grid[i_max]
            shift_opt = shift_grid[i_max]

            # readjust grid for next iteration_reduce_range_factor
            _scale = scale_opt + _scale_range * np.diff(_scale) * self._reduce_range_factor
            _shift = shift_opt + _scale_range * np.diff(_shift) * self._reduce_range_factor
        return shift_opt, scale_opt

    def apply(self, return_shifts: bool = None):
        """Align the signals against the computed values"""
        if not self._computed:
            warnings.warn("Aligning data without computing optimal alignment parameters", UserWarning)
        self._return_shifts = return_shifts if return_shifts is not None else self._return_shifts

        if self._only_shift:
            self.shift()
        else:
            self.align()

        # return aligned data and shifts
        if self._return_shifts:
            return self.array_aligned, self.shift_values
        # only return data
        return self.array_aligned

    def align(self, shift_opt=None, scale_opt=None):
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
            self.array_aligned[iteration] = self._apply(y, shift_opt[iteration], scale_opt[iteration])
        self.shift_values = self.shift_opt

        LOGGER.debug(f"Re-aligned {self.n_signals} signals " + time_loop(t_start, self.n_signals + 1, self.n_signals))

    def _apply(self, y: np.ndarray, shift_value: float, scale_value: float):
        """Apply alignment correction to array `y`."""
        func = generate_function(self.method, (self.x - shift_value) / scale_value, y)
        return np.nan_to_num(func(self.x))

    def shift(self, shift_opt=None):
        """Quickly shift array based on the optimized shift parameters.

        This method does not interpolate but rather moves the data left and right without applying any scaling.

        Parameters
        ----------
        shift_opt: Optional[np.ndarray]
            vector containing values by which to shift the array
        """
        t_start = time.time()
        if shift_opt is None:
            shift_opt = np.round(self.shift_opt).astype(np.int32)

        # quickly shift based on provided values
        for iteration, y in enumerate(self.array):
            self.array_aligned[iteration] = self._shift(y, shift_opt[iteration])
        self.shift_values = shift_opt

        LOGGER.debug(f"Re-aligned {self.n_signals} signals " + time_loop(t_start, self.n_signals + 1, self.n_signals))

    @staticmethod
    def _shift(y: np.ndarray, shift_value: float):
        """Apply shift correction to array `y`."""
        return shift(y, -int(shift_value))

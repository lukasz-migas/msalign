"""Test functions"""

import numpy as np
import scipy.interpolate as interpolate
from numpy.testing import assert_equal, assert_raises
from scipy import signal
from scipy.ndimage import shift

from msalign import check_xy, generate_function, msalign


class Test_generate_function(object):
    """Test generate_function"""

    @staticmethod
    def test_generate_function_pchip():
        """Test pchip function generator"""
        f = generate_function("pchip", [1, 2, 3], [3, 2, 1])
        assert isinstance(f, interpolate.PchipInterpolator)

    @staticmethod
    def test_generate_function_interp1d():
        """Test other interpolation function generator"""
        f = generate_function("zero", [1, 2, 3], [3, 2, 1])
        assert isinstance(f, interpolate.interp1d)


class Test_check_xy(object):
    """Test check_xy"""

    @staticmethod
    def test_check_xy_correct():
        """Check that data orientation will be correctly set"""
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (20, 10))
        zvals_out = check_xy(xvals, zvals_in)
        assert_equal(zvals_in, zvals_out)

    @staticmethod
    def test_check_xy_incorrect():
        """Check that data orientation will be correctly set"""
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (10, 20))
        zvals_out = check_xy(xvals, zvals_in)
        assert_equal(zvals_in.T, zvals_out)

    @staticmethod
    def test_check_xy_invalid():
        """Check that the function will raise an error if incorrectly shaped data is parsed in"""
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (11, 20))
        assert_raises(ValueError, check_xy, xvals, zvals_in)


class Test_msalign(object):
    """Check msalign"""

    @staticmethod
    def test_msalign_parameters_invalid():
        """Make sure that parameters will be always be correct"""
        xvals = np.arange(10)
        zvals = np.random.randint(0, 100, (20, 10))
        assert_raises(TypeError, msalign, xvals, zvals, 10)
        assert_raises(ValueError, msalign, xvals, zvals, [10], method="method")
        assert_raises(ValueError, msalign, xvals, zvals, [10], weights=[10, 10])
        assert_raises(ValueError, msalign, xvals, zvals, [10], iterations=0)
        assert_raises(TypeError, msalign, xvals, zvals, [10], iterations=1.)
        assert_raises(ValueError, msalign, xvals, zvals, [10], shift_range=[-10])
        assert_raises(ValueError, msalign, xvals, zvals, [10], shift_range=[10, 10])
        assert_raises(ValueError, msalign, xvals, zvals, [10], ratio=0)
        assert_raises(ValueError, msalign, xvals, zvals, [10], grid_steps=0)
        assert_raises(ValueError, msalign, xvals, zvals, [10], resolution=0)
        assert_raises(ValueError, msalign, xvals, zvals, [10, 20], only_shift="HelloWorld")
        assert_raises(ValueError, msalign, xvals, zvals, [10, 20], return_shifts="HelloWorld")

    @staticmethod
    def test_msalign_run():
        # generate synthetic dataset
        n_points = 100
        n_signals = 5
        noise = 0
        shifts = np.arange(1, n_signals)
        xvals = np.arange(n_points)

        # the first signal is 'real' and we should align to that
        synthetic_signal = np.zeros((n_signals, n_points))
        synthetic_signal[0] = signal.gaussian(n_points, std=4) + np.random.normal(0, noise, n_points)

        # determine the major peak by which msalign should align
        alignment_peak = synthetic_signal[0].argmax()

        # apply shift pattern
        for i in range(1, n_signals):
            synthetic_signal[i] = shift(signal.gaussian(n_points, std=4), shifts[i - 1]) + \
                np.random.normal(0, noise, n_points)

        # align using msalign
        synthetic_signal_shifted = msalign(xvals, synthetic_signal, [alignment_peak])
        signal_difference = np.sum(synthetic_signal_shifted) - np.sum(synthetic_signal)
        assert signal_difference < 0.001

"""Test functions"""

from msalign import generate_function, check_xy, msalign
import scipy.interpolate as interpolate
import numpy as np
from numpy.testing import assert_equal, assert_raises


class Test_generate_function(object):
    """Test generate_function"""

    @staticmethod
    def test_generate_function_pchip():
        f = generate_function("pchip", [1, 2, 3], [3, 2, 1])
        assert isinstance(f, interpolate.PchipInterpolator)

    @staticmethod
    def test_generate_function_interp1d():
        f = generate_function("zero", [1, 2, 3], [3, 2, 1])
        assert isinstance(f, interpolate.interp1d)


class Test_check_xy(object):
    """Test check_xy"""

    @staticmethod
    def test_check_xy_correct():
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (20, 10))
        zvals_out = check_xy(xvals, zvals_in)
        assert_equal(zvals_in, zvals_out)

    @staticmethod
    def test_check_xy_incorrect():
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (10, 20))
        zvals_out = check_xy(xvals, zvals_in)
        assert_equal(zvals_in.T, zvals_out)

    @staticmethod
    def test_check_xy_invalid():
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (11, 20))
        assert_raises(ValueError, check_xy, xvals, zvals_in)


class Test_msalign(object):

    @staticmethod
    def test_msalign_parameters_invalid():
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

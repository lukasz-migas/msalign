"""Test functions"""

from msalign import generate_function, check_xy
import scipy.interpolate as interpolate
import numpy as np
from numpy.testing import assert_equal


class Test_generate_function(object):
    """Test generate_function"""

    @staticmethod
    def test_generate_function_pchip(self):
        f = generate_function("pchip", [1, 2, 3], [3, 2, 1])
        assert isinstance(f, interpolate.PchipInterpolator)

    @staticmethod
    def test_generate_function_interp1d(self):
        f = generate_function("zero", [1, 2, 3], [3, 2, 1])
        assert isinstance(f, interpolate.interp1d)


class Test_check_xy(object):
    """Test check_xy"""

    @staticmethod
    def test_check_xy_correct(self):
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (20, 10))
        zvals_out = check_xy(xvals, zvals_in)
        assert_equal(zvals_in, zvals_out)

    @staticmethod
    def test_check_xy_incorrect(self):
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (10, 20))
        zvals_out = check_xy(xvals, zvals_in)
        assert_equal(zvals_in.T, zvals_out)

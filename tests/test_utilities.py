"""Utilities."""
import numpy as np
import pytest
import scipy.interpolate as interpolate
from numpy.testing import assert_array_equal, assert_equal

from msalign.utilities import (
    check_xy,
    convert_peak_values_to_index,
    find_nearest_index,
    format_time,
    generate_function,
    shift,
)


class TestShift:
    """Test shift"""

    @staticmethod
    @pytest.mark.parametrize("num", (-3.0, np.inf))
    def test_shift_fail(num):
        y = np.arange(10)
        with pytest.raises(ValueError):
            shift(y, num)

    @staticmethod
    def test_shift_none():
        y = np.arange(10)
        y_new = shift(y, 0)
        assert_array_equal(y, y_new)

    @staticmethod
    @pytest.mark.parametrize("fill_value", (0, 100))
    def test_shift_plus(fill_value):
        y = np.arange(1, 10)
        y_new = shift(y, 1, fill_value)
        assert y_new[0] == fill_value

    @staticmethod
    @pytest.mark.parametrize("fill_value", (0, 100))
    def test_shift_minus(fill_value):
        y = np.arange(1, 10)
        y_new = shift(y, -1, fill_value)
        assert y_new[-1] == fill_value


class TestFindNearestIndex:
    """Test find_nearest_index"""

    @staticmethod
    def test_find_nearest_index():
        xvals = np.arange(10)
        correct_index = 3
        return_index = find_nearest_index(xvals, 3)
        assert correct_index == return_index


class TestConvertPeaksToIndex:
    """Test"""

    @staticmethod
    def test_convert_peak_values_to_index():
        x = np.linspace(0, 10, 100, endpoint=False)
        peaks = [0.0, 1.0, 9.0]
        expected_idx = [0, 10, 90]
        returned_idx = convert_peak_values_to_index(x, peaks)

        assert expected_idx == returned_idx


class TestGenerateInterpolationFunction:
    """Test generate_function"""

    @staticmethod
    def test_generate_function_pchip():
        """Test pchip function generator"""
        fcn = generate_function("pchip", [1, 2, 3], [3, 2, 1])
        assert isinstance(fcn, interpolate.PchipInterpolator)

    @staticmethod
    def test_generate_function_interp1d():
        """Test other interpolation function generator"""
        fcn = generate_function("zero", [1, 2, 3], [3, 2, 1])
        assert isinstance(fcn, interpolate.interp1d)


class TestCheckXY:
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
        with pytest.warns(UserWarning):
            zvals_out = check_xy(xvals, zvals_in)
        assert_equal(zvals_in.T, zvals_out)

    @staticmethod
    def test_check_xy_invalid():
        """Check that the function will raise an error if incorrectly shaped data is parsed in"""
        xvals = np.arange(10)
        zvals_in = np.random.randint(0, 100, (11, 20))
        with pytest.raises(ValueError):
            check_xy(xvals, zvals_in)


@pytest.mark.parametrize(
    "value, expected",
    [(0.004, "us"), (0.1, "ms"), (0.5, "s"), (1, "s"), (60, "s"), (75, "min"), (3654, "hr"), (86414, "day")],
)
def test_format_time(value, expected):
    """Test 'format_time'"""
    result = format_time(value)
    assert expected in result

"""Test functions"""

from msalign import generate_function
import scipy.interpolate as interpolate


class TestGenerateFunction(object):
    """Test __generate_function"""

    def test_generate_function_pchip(self):
        f = generate_function("pchip", [1, 2, 3], [3, 2, 1])
        assert isinstance(f, interpolate.PchipInterpolator)

    def test_generate_function_interp1d(self):
        f = generate_function("zero", [1, 2, 3], [3, 2, 1])
        assert isinstance(f, interpolate.interp1d)

"""Test functions"""
import numpy as np
import pytest
from scipy import signal
from scipy.ndimage import shift

import msalign


@pytest.fixture
def make_data():
    """Function to make data."""

    def _wrap():
        x = np.arange(10)
        array = np.random.randint(0, 100, (20, 10))
        return x, array

    return _wrap


class TestMSalign:
    """Test msalign"""

    @pytest.mark.parametrize("peaks", (10, -10))
    def test_msalign_parameters_invalid_peaks(self, make_data, peaks):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(TypeError):
            msalign.msalign(x, array, peaks)

    @pytest.mark.parametrize("method", ("method", "pChIp", "LINEAR"))
    def test_msalign_parameters_invalid_method(self, make_data, method):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], method=method)

    @pytest.mark.parametrize("weights", ([10, 10], 10))
    def test_msalign_parameters_invalid_weights(self, make_data, weights):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], weights=weights)

    @pytest.mark.parametrize("iterations", (-1, 0, 0.0, 2.3))
    def test_msalign_parameters_invalid_iterations(self, make_data, iterations):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], iterations=iterations)

    @pytest.mark.parametrize("shift_range", ([-10], [10, 10]))
    def test_msalign_parameters_invalid_shift_range(self, make_data, shift_range):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()

        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], shift_range=shift_range)

    @pytest.mark.parametrize("ratio", (0, -3))
    def test_msalign_parameters_invalid_ratio(self, make_data, ratio):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()

        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], ratio=ratio)

    @pytest.mark.parametrize("grid_steps", (0, -3))
    def test_msalign_parameters_invalid_grid_steps(self, make_data, grid_steps):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], grid_steps=grid_steps)

    @pytest.mark.parametrize("resolution", (0, -3))
    def test_msalign_parameters_invalid_resolution(self, make_data, resolution):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], resolution=resolution)

    @pytest.mark.parametrize("only_shift", ("True", "False"))
    def test_msalign_parameters_invalid_only_shift(self, make_data, only_shift):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10, 20], only_shift=only_shift)

    @pytest.mark.parametrize("return_shifts", ("True", "False"))
    def test_msalign_parameters_invalid_return_shifts(self, make_data, return_shifts):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10, 20], return_shifts=return_shifts)

    @pytest.mark.parametrize("align_by_index", ("True", "False"))
    def test_msalign_parameters_invalid_align_by_index(self, make_data, align_by_index):
        """Make sure that parameters will be always be correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], align_by_index=align_by_index)

    @pytest.mark.parametrize("noise", (0, 1e-5, 1e-3))
    @pytest.mark.parametrize("align_by_index", (True, False))
    @pytest.mark.parametrize("method", ("pchip", "cubic"))
    @pytest.mark.parametrize("n_shift", (0, 1, 3, 5, 7))
    def test_msalign_run(self, noise, align_by_index, method, n_shift):
        n_points = 100
        n_signals = 5
        shifts = np.arange(0, n_signals) * n_shift
        x = np.arange(n_points)

        array = np.zeros((n_signals, n_points))
        gaussian = signal.gaussian(n_points, std=4) + np.random.normal(0, noise, n_points)
        alignment_peak = gaussian.argmax()

        for i in range(n_signals):
            array[i] = shift(gaussian, shifts[i]) + np.random.normal(0, noise, n_points)

        # align using msalign
        aligned_array, shifts_out = msalign.msalign(
            x, array, [alignment_peak], return_shifts=True, align_by_index=align_by_index, method=method
        )
        signal_difference = np.sum(aligned_array) - np.sum(array)
        aligned_alignment_peak = aligned_array[0].argmax()

        assert shifts_out.shape[0] == n_signals
        assert (alignment_peak - aligned_alignment_peak) < 0.001
        assert signal_difference < 0.1

    @pytest.mark.parametrize("only_shift", (True, False))
    def test_msalign_only_shift(self, only_shift):
        n_points = 100
        n_signals = 5
        shifts = np.arange(0, n_signals)
        x = np.arange(n_points)

        array = np.zeros((n_signals, n_points))
        gaussian = signal.gaussian(n_points, std=4) + np.random.normal(0, 0, n_points)
        alignment_peak = gaussian.argmax()

        for i in range(n_signals):
            array[i] = shift(gaussian, shifts[i]) + np.random.normal(0, 0, n_points)

        # align using msalign
        aligned_array = msalign.msalign(
            x, array, [alignment_peak], return_shifts=False, align_by_index=True, only_shift=only_shift
        )
        signal_difference = np.sum(aligned_array) - np.sum(array)
        aligned_alignment_peak = aligned_array[0].argmax()

        assert (alignment_peak - aligned_alignment_peak) <= 1
        assert signal_difference < 0.1

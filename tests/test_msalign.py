"""Test functions"""
import numpy as np
import pytest
from scipy import signal
from scipy.ndimage import shift

import msalign


@pytest.fixture
def data():
    x = np.arange(10)
    array = np.random.randint(0, 100, (20, 10))
    return x, array


class TestMSalign(object):
    """Test msalign"""

    @staticmethod
    @pytest.mark.parametrize("peaks", (10, -10))
    def test_msalign_parameters_invalid_peaks(data, peaks):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(TypeError):
            msalign.msalign(x, array, peaks)

    @staticmethod
    @pytest.mark.parametrize("method", ("method", "pChIp", "LINEAR"))
    def test_msalign_parameters_invalid_method(data, method):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], method=method)

    @staticmethod
    @pytest.mark.parametrize("weights", ([10, 10], 10))
    def test_msalign_parameters_invalid_weights(data, weights):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], weights=weights)

    @staticmethod
    @pytest.mark.parametrize("iterations", (-1, 0, 0.0, 2.3))
    def test_msalign_parameters_invalid_iterations(data, iterations):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], iterations=iterations)

    @staticmethod
    @pytest.mark.parametrize("shift_range", ([-10], [10, 10]))
    def test_msalign_parameters_invalid_shift_range(data, shift_range):
        """Make sure that parameters will be always be correct"""
        x, array = data

        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], shift_range=shift_range)

    @staticmethod
    @pytest.mark.parametrize("ratio", (0, -3))
    def test_msalign_parameters_invalid_ratio(data, ratio):
        """Make sure that parameters will be always be correct"""
        x, array = data

        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], ratio=ratio)

    @staticmethod
    @pytest.mark.parametrize("grid_steps", (0, -3))
    def test_msalign_parameters_invalid_grid_steps(data, grid_steps):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], grid_steps=grid_steps)

    @staticmethod
    @pytest.mark.parametrize("resolution", (0, -3))
    def test_msalign_parameters_invalid_resolution(data, resolution):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], resolution=resolution)

    @staticmethod
    @pytest.mark.parametrize("only_shift", ("True", "False"))
    def test_msalign_parameters_invalid_only_shift(data, only_shift):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10, 20], only_shift=only_shift)

    @staticmethod
    @pytest.mark.parametrize("return_shifts", ("True", "False"))
    def test_msalign_parameters_invalid_return_shifts(data, return_shifts):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10, 20], return_shifts=return_shifts)

    @staticmethod
    @pytest.mark.parametrize("align_by_index", ("True", "False"))
    def test_msalign_parameters_invalid_align_by_index(data, align_by_index):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], align_by_index=align_by_index)

    @staticmethod
    def test_msalign_parameters_invalid_quick_only(data):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [100], only_shift=False, quick_shift=True)

    @staticmethod
    def test_msalign_parameters_invalid_quick_index(data):
        """Make sure that parameters will be always be correct"""
        x, array = data
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [100], align_by_index=False, quick_shift=True)

    @staticmethod
    @pytest.mark.parametrize("noise", (0, 1e-5, 1e-3))
    @pytest.mark.parametrize("align_by_index", (True, False))
    @pytest.mark.parametrize("method", ("pchip", "cubic"))
    @pytest.mark.parametrize("n_shift", (0, 1, 3, 5, 7))
    def test_msalign_run(noise, align_by_index, method, n_shift):
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

    @staticmethod
    @pytest.mark.parametrize("quick_shift", (True, False))
    def test_msalign_quick_shift(quick_shift):
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
            x, array, [alignment_peak], return_shifts=False, align_by_index=True, quick_shift=quick_shift
        )
        signal_difference = np.sum(aligned_array) - np.sum(array)
        aligned_alignment_peak = aligned_array[0].argmax()

        assert shifts_out.shape[0] == n_signals
        assert (alignment_peak - aligned_alignment_peak) <= 1
        assert signal_difference < 0.1

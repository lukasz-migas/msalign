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
        """Make sure that parameters are always correct"""
        x, array = make_data()
        with pytest.raises(TypeError):
            msalign.msalign(x, array, peaks)

    @pytest.mark.parametrize("method", ("method", "pChIp", "LINEAR"))
    def test_msalign_parameters_invalid_method(self, make_data, method):
        """Make sure that parameters are always correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], method=method)

    @pytest.mark.parametrize("weights", ([10, 10], 10))
    def test_msalign_parameters_invalid_weights(self, make_data, weights):
        """Make sure that parameters are always correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], weights=weights)

    @pytest.mark.parametrize("iterations", (-1, 0, 0.0, 2.3))
    def test_msalign_parameters_invalid_iterations(self, make_data, iterations):
        """Make sure that parameters are always correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], iterations=iterations)

    @pytest.mark.parametrize("shift_range", ([-10], [10, 10]))
    def test_msalign_parameters_invalid_shift_range(self, make_data, shift_range):
        """Make sure that parameters are always correct"""
        x, array = make_data()

        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], shift_range=shift_range)

    @pytest.mark.parametrize("ratio", (0, -3))
    def test_msalign_parameters_invalid_ratio(self, make_data, ratio):
        """Make sure that parameters are always correct"""
        x, array = make_data()

        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], ratio=ratio)

    @pytest.mark.parametrize("grid_steps", (0, -3))
    def test_msalign_parameters_invalid_grid_steps(self, make_data, grid_steps):
        """Make sure that parameters are always correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], grid_steps=grid_steps)

    @pytest.mark.parametrize("resolution", (0, -3))
    def test_msalign_parameters_invalid_resolution(self, make_data, resolution):
        """Make sure that parameters are always correct"""
        x, array = make_data()
        with pytest.raises(ValueError):
            msalign.msalign(x, array, [10], resolution=resolution)

    @pytest.mark.parametrize("noise", (0, 1e-5, 1e-3))
    @pytest.mark.parametrize("align_by_index", (True, False))
    @pytest.mark.parametrize("method", ("pchip", "cubic"))
    def test_msalign_run_no_shift(self, noise, align_by_index, method):
        n_points = 100
        n_signals = 5
        shifts = np.arange(0, n_signals) * 0
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
        signal_difference = np.abs(np.sum(aligned_array) - np.sum(array))

        assert signal_difference < 0.1
        for y in aligned_array:
            aligned_alignment_peak = y.argmax()
            assert (alignment_peak - aligned_alignment_peak) <= 1.001
        assert shifts_out.shape[0] == n_signals

    @pytest.mark.parametrize("noise", (0, 1e-5, 1e-3))
    @pytest.mark.parametrize("align_by_index", (True, False))
    @pytest.mark.parametrize("method", ("pchip", "cubic"))
    @pytest.mark.parametrize("n_shift", (1, 3, 5, 7))
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
        signal_difference = np.abs(np.sum(aligned_array) - np.sum(array))

        assert shifts_out.shape[0] == n_signals
        for y in aligned_array:
            aligned_alignment_peak = y.argmax()
            assert (alignment_peak - aligned_alignment_peak) <= 1.001
            assert signal_difference < 0.1

    @pytest.mark.parametrize("noise", (0, 1e-5, 1e-3))
    @pytest.mark.parametrize("only_shift", (True, False))
    def test_msalign_only_shift(self, only_shift, noise):
        n_points = 500
        n_signals = 5
        shifts = np.arange(0, n_signals)
        x = np.arange(n_points)

        array = np.zeros((n_signals, n_points))
        gaussian_1 = signal.gaussian(n_points, std=4) + np.random.normal(0, noise, n_points)
        gaussian_2 = shift(signal.gaussian(n_points, std=4) + np.random.normal(0, noise, n_points), 100) * 0.5
        gaussian = gaussian_1 + gaussian_2
        alignment_peaks = [gaussian_1.argmax(), gaussian_2.argmax()]

        for i in range(n_signals):
            array[i] = shift(gaussian, shifts[i]) + np.random.normal(0, 0, n_points)

        # align using msalign
        aligned_array = msalign.msalign(
            x,
            array,
            alignment_peaks,
            return_shifts=False,
            align_by_index=True,
            only_shift=only_shift,
            width=2.5,
            ratio=0.5,
        )
        signal_difference = np.abs(np.sum(aligned_array) - np.sum(array))

        assert signal_difference < 1
        for y in aligned_array:
            aligned_alignment_peak = y.argmax()
            assert (alignment_peaks[0] - aligned_alignment_peak) <= 1.001

    def test_msalign_empty_array(self):
        peaks = [5, 10]
        x = np.arange(100)
        aligner = msalign.Aligner(x, None, peaks)
        assert aligner.n_peaks == 2
        assert aligner.n_signals == 0

    @pytest.mark.parametrize("n_shift", (1, 3, 5, 7))
    def test_aligner_run(self, n_shift):
        n_points = 100
        n_signals = 5
        shifts = np.arange(0, n_signals) * n_shift
        x = np.arange(n_points)

        array = np.zeros((n_signals, n_points))
        gaussian = signal.gaussian(n_points, std=4) + np.random.normal(0, 1e-5, n_points)
        alignment_peak = gaussian.argmax()

        for i in range(n_signals):
            array[i] = shift(gaussian, shifts[i]) + np.random.normal(0, 1e-5, n_points)

        # align using msalign
        aligner = msalign.Aligner(x, array, [alignment_peak], return_shifts=True, only_shift=True)
        aligner.run()
        aligned_array, _ = aligner.apply()
        signal_difference = np.abs(np.sum(aligned_array) - np.sum(array))

        assert signal_difference < 0.1
        for y in aligned_array:
            aligned_alignment_peak = y.argmax()
            assert (alignment_peak - aligned_alignment_peak) <= 1.001

        # run in iterator mode
        shifts, scales = [], []
        for y in array:
            shift_value, scale_value = aligner.compute(y)
            shifts.append(shift_value)
            scales.append(scale_value)

        np.testing.assert_array_almost_equal(shifts, aligner.shift_opt.flatten())
        np.testing.assert_array_almost_equal(scales, aligner.scale_opt.flatten())

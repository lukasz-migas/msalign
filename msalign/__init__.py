"""Signal calibration and alignment by reference peaks - copy of MSALIGN function from MATLAB bioinformatics library."""
# Standard library imports
from typing import List

# Third-party imports
import numpy as np

# Local imports
from msalign.align import Aligner
from msalign._version import __version__  # noqa

__all__ = ["msalign", "Aligner"]


def msalign(
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
    aligner = Aligner(
        x,
        array,
        peaks,
        method=method,
        width=width,
        ratio=ratio,
        resolution=resolution,
        iterations=iterations,
        grid_steps=grid_steps,
        shift_range=shift_range,
        weights=weights,
        return_shifts=return_shifts,
        align_by_index=align_by_index,
        only_shift=only_shift,
        quick_shift=quick_shift,
    )
    aligner.run()
    return aligner.align()


msalign.__doc__ = Aligner.__doc__

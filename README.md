# msalign - signal calibration and alignment

This package was inspired by MATLAB's [msalign](https://nl.mathworks.com/help/bioinfo/ref/msalign.html) function which
allows alignment of multiple signals to reference peaks.

## Installation

```python
pip install git+https://github.com/lukasz-migas/msalign.git
```

## Usage
Usage is relatively straightforward. Simply import the function `msalign` from the package and provide `xvals`, `zvals`
and `peaks`. Other parameters can be passed-in using `kwargs`.

```python
import numpy as np
from msalign import msalign


fname = r"./example_data/msalign_test_data.csv"
data = np.genfromtxt(fname, delimiter=",")
xvals = data[1:, 0]
zvals = data[1:, 1:].T

peaks = [3991.4, 4598, 7964, 9160]
kwargs = dict(
    iterations=5, 
    weights=[60, 100, 60, 100], 
    resolution=100, 
    grid_steps=20, 
    ratio=2.5, 
    shift_range=[-100, 100],
    )

zvals_new = msalign(xvals, zvals, peaks, **kwargs)
```
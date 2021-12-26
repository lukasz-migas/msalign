# msalign - signal calibration and alignment

[![Tests](https://github.com/lukasz-migas/msalign/workflows/Tests/badge.svg)](https://github.com/lukasz-migas/msalign/actions)
[![codecov](https://codecov.io/gh/lukasz-migas/msalign/branch/master/graph/badge.svg)](https://codecov.io/gh/lukasz-migas/msalign)
[![CodeFactor](https://www.codefactor.io/repository/github/lukasz-migas/msalign/badge)](https://www.codefactor.io/repository/github/lukasz-migas/msalign)
[![Netlify Status](https://api.netlify.com/api/v1/badges/921b7fdf-99e2-4019-84a0-3ad61729f2cc/deploy-status)](https://app.netlify.com/sites/msalign/deploys)

[![Wheel](https://img.shields.io/pypi/wheel/msalign.svg)](https://pypi.org/project/msalign/)
[![PyPI](https://img.shields.io/pypi/v/msalign.svg)](https://pypi.org/project/msalign/)
[![Versions](https://img.shields.io/pypi/pyversions/msalign.svg)](https://pypi.org/project/msalign/)
[![Downloads](https://pepy.tech/badge/msalign)](https://pepy.tech/project/msalign)

This package was inspired by MATLAB's [msalign](https://mathworks.com/help/bioinfo/ref/msalign.html) function which
allows alignment of multiple signals to reference peaks.

## Installation

Install from PyPi

```python
pip install msalign
```

Install directly from GitHub

```python
pip install -e git+https://github.com/lukasz-migas/msalign.git
```

Install in development mode

```python
python setup.py develop
```

## Usage

Usage is relatively straightforward. Simply import `msalign` from the package and provide `x`, `array`
and `peaks` values. `msalign` accepts a lot of other parameters that might improve your alignment - simply provide them
as `keyword` parameters.

```python
import numpy as np
from msalign import msalign


filename = r"./example_data/msalign_test_data.csv"
data = np.genfromtxt(filename, delimiter=",")
x = data[1:, 0]
array = data[1:, 1:].T
peaks = [3991.4, 4598, 7964, 9160]

aligned = msalign(x, array, peaks, weights=[60, 100, 60, 100], only_shift=False)
```

![png](docs/img/ms-spectrum.png)

Zoom-in on each peak the spectrum was aligned against

![png](docs/img/ms-peaks.png)

## Reference

Monchamp, P., Andrade-Cetto, L., Zhang, J.Y., and Henson, R. (2007) Signal Processing Methods for Mass
Spectrometry. In Systems Bioinformatics: An Engineering Case-Based Approach, G. Alterovitz and M.F. Ramoni, eds.
Artech House Publishers).

[MATLAB's msalign](https://mathworks.com/help/bioinfo/ref/msalign.html)

# msalign - signal calibration and alignment

[![Build Status](https://travis-ci.com/lukasz-migas/msalign.svg?branch=master)](https://travis-ci.com/lukasz-migas/msalign)
[![codecov](https://codecov.io/gh/lukasz-migas/msalign/branch/master/graph/badge.svg)](https://codecov.io/gh/lukasz-migas/msalign)
[![Requirements Status](https://requires.io/github/lukasz-migas/msalign/requirements.svg?branch=master)](https://requires.io/github/lukasz-migas/msalign/requirements/?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/lukasz-migas/msalign/badge)](https://www.codefactor.io/repository/github/lukasz-migas/msalign)
[![Netlify Status](https://api.netlify.com/api/v1/badges/921b7fdf-99e2-4019-84a0-3ad61729f2cc/deploy-status)](https://app.netlify.com/sites/msalign/deploys)

[![Wheel](https://img.shields.io/pypi/wheel/msalign.svg)](https://pypi.org/project/msalign/)
[![Versions](https://img.shields.io/pypi/pyversions/msalign.svg)](https://pypi.org/project/msalign/)

This package was inspired by MATLAB's [msalign](https://mathworks.com/help/bioinfo/ref/msalign.html) function which
allows alignment of multiple signals to reference peaks.

## Installation

```python
pip install msalign
```

or

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

## Reference

Monchamp, P., Andrade-Cetto, L., Zhang, J.Y., and Henson, R. (2007) Signal Processing Methods for Mass
Spectrometry. In Systems Bioinformatics: An Engineering Case-Based Approach, G. Alterovitz and M.F. Ramoni, eds.
Artech House Publishers).

[MATLAB's msalign](https://mathworks.com/help/bioinfo/ref/msalign.html)
# Welcome

[![Tests](https://github.com/lukasz-migas/msalign/workflows/Tests/badge.svg)](https://github.com/lukasz-migas/msalign/actions)
[![codecov](https://codecov.io/gh/lukasz-migas/msalign/branch/master/graph/badge.svg)](https://codecov.io/gh/lukasz-migas/msalign)
[![Requirements Status](https://requires.io/github/lukasz-migas/msalign/requirements.svg?branch=master)](https://requires.io/github/lukasz-migas/msalign/requirements/?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/lukasz-migas/msalign/badge)](https://www.codefactor.io/repository/github/lukasz-migas/msalign)
[![Netlify Status](https://api.netlify.com/api/v1/badges/921b7fdf-99e2-4019-84a0-3ad61729f2cc/deploy-status)](https://app.netlify.com/sites/msalign/deploys)

[![Wheel](https://img.shields.io/pypi/wheel/msalign.svg)](https://pypi.org/project/msalign/)
[![PyPI](https://img.shields.io/pypi/v/msalign.svg)](https://pypi.org/project/msalign/)
[![Versions](https://img.shields.io/pypi/pyversions/msalign.svg)](https://pypi.org/project/msalign/)
[![Downloads](https://pepy.tech/badge/msalign)](https://pepy.tech/project/msalign)

This package was inspired by MATLAB's [msalign](https://mathworks.com/help/bioinfo/ref/msalign.html) function which
allows alignment of multiple signals to reference peaks.

## Quick installation

```python
pip install msalign
```

## Quick usage

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

![png](img/ms-spectrum.png)

Zoom-in on each peak the spectrum was aligned against

![png](img/ms-peaks.png)

## Example alignment

In the [Examples](examples/msalign-mass-spectrum.md) you will find a couple of examples that showcase the performance of `msalign`
against synthetic and real examples.

![png](img/multi-gaussian.png)
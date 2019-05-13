# Welcome

[![Build Status](https://travis-ci.com/lukasz-migas/msalign.svg?branch=master)](https://travis-ci.com/lukasz-migas/msalign)
[![codecov](https://codecov.io/gh/lukasz-migas/msalign/branch/master/graph/badge.svg)](https://codecov.io/gh/lukasz-migas/msalign)
[![Requirements Status](https://requires.io/github/lukasz-migas/msalign/requirements.svg?branch=master)](https://requires.io/github/lukasz-migas/msalign/requirements/?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/lukasz-migas/msalign/badge)](https://www.codefactor.io/repository/github/lukasz-migas/msalign)
[![Netlify Status](https://api.netlify.com/api/v1/badges/921b7fdf-99e2-4019-84a0-3ad61729f2cc/deploy-status)](https://app.netlify.com/sites/msalign/deploys)

[![Wheel](https://img.shields.io/pypi/wheel/msalign.svg)](https://pypi.org/project/msalign/)
[![Versions](https://img.shields.io/pypi/pyversions/msalign.svg)](https://pypi.org/project/msalign/)

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


fname = r"./example_data/msalign_test_data.csv"
data = np.genfromtxt(fname, delimiter=",")
xvals = data[1:, 0]
zvals = data[1:, 1:].T

peaks = [3991.4, 4598, 7964, 9160]
kwargs = dict(
    weights=[60, 100, 60, 100],
    only_shift=False,
    )

zvals_new = msalign(xvals, zvals, peaks, **kwargs)
```

## Example alignment

In the [Usage](main/usage.md) section you will find a couple of examples of signal alignment based on single or multiple
reference peaks.

![img](img/noisy_synthetic_signal_before_and_after.png)

#!/usr/bin/env python
#
# Copyright (C) 2019 Lukasz Migas

DESCRIPTION = "msalign: Signal calibration and alignment by reference peaks"
LONG_DESCRIPTION = """\
"""

DISTNAME = "msalign"
MAINTAINER = "Lukasz Migas"
MAINTAINER_EMAIL = "lukas.migas@yahoo.com"
# URL = ''
LICENSE = "Apache license 2.0"
DOWNLOAD_URL = "https://github.com/lukasz-migas/msalign"
VERSION = "0.0.1"

INSTALL_REQUIRES = ["numpy>=1.9.3", "scipy>=0.14.0"]

PACKAGES = ["msalign"]

CLASSIFIERS = [
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS",
    "Operating System :: Microsoft :: Windows",
    "Natural Language :: English",
]

try:
    from setuptools import setup

    _has_setuptools = True
except ImportError:
    from distutils.core import setup

if __name__ == "__main__":

    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        # url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        install_requires=INSTALL_REQUIRES,
        packages=PACKAGES,
        classifiers=CLASSIFIERS,
        package_dir={"msalign": "msalign"},
    )
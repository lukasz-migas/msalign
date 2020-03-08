#!/usr/bin/env python
#
# Copyright (C) 2020 Lukasz Migas

from _setup_support import read_requirements

DESCRIPTION = "msalign: Signal calibration and alignment by reference peaks"

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

DISTNAME = "msalign"
MAINTAINER = "Lukasz Migas"
MAINTAINER_EMAIL = "lukas.migas@yahoo.com"
URL = "https://github.com/lukasz-migas/msalign"
LICENSE = "Apache license 2.0"
DOWNLOAD_URL = "https://github.com/lukasz-migas/msalign"
INSTALL_REQUIRES = read_requirements("requirements/requirements-std.txt")

PACKAGES = ["msalign"]

CLASSIFIERS = [
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS",
    "Operating System :: Microsoft :: Windows",
    "Natural Language :: English",
]

try:
    from setuptools import setup
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
        long_description_content_type="text/markdown",
        license=LICENSE,
        url=URL,
        download_url=DOWNLOAD_URL,
        install_requires=INSTALL_REQUIRES,
        use_scm_version=True,
        setup_requires=["setuptools_scm"],
        packages=PACKAGES,
        classifiers=CLASSIFIERS,
        package_dir={"msalign": "msalign"},
    )

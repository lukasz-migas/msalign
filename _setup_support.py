# Standard library imports
from typing import List
import re


def get_version():
    version_file = "msalign/_version.py"
    ver_str_line = open(version_file, "rt").read()
    ver_str_raw = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(ver_str_raw, ver_str_line, re.M)
    if mo:
        ver_str_raw = mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (version_file,))

    return ver_str_raw


def read_requirements(path: str) -> List:
    """Read requirements file and if necessary and sub-files

    Parameters
    ----------
    path : str

    Returns
    -------
    install : List
        list of packages to be installed by the setup.py script
    """

    def process_line(line):
        if line.startswith("-r"):
            return get_file_contents(line)
        if line.startswith("#"):
            return None
        if line.startswith("-e"):
            return line
        return line

    # read requirements
    _install = get_file_contents(path)
    install = []
    for line in _install:
        processed_line = process_line(line)
        if processed_line is None:
            continue
        elif isinstance(processed_line, list):
            for _line in processed_line:
                _processed_line = process_line(_line)
                if _line is None:
                    continue
                elif isinstance(_line, str):
                    install.append(_line)
        elif isinstance(line, str):
            install.append(line)
    return install


def get_file_contents(filename):
    with open(filename) as f:
        _install = f.read().splitlines()

    return _install

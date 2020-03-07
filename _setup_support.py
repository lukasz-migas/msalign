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

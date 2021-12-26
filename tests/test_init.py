"""Tests."""
from msalign import __version__


def test_version():
    assert isinstance(__version__, str)


def test_import():
    from msalign import msalign

    assert callable(msalign)

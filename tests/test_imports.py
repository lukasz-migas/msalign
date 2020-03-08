"""Test modules importation."""


def test_import_numpy():
    """Import NumPy."""
    import numpy

    del numpy


def test_import_scipy():
    """Import scipy."""
    import scipy

    del scipy


def test_import_msalign():
    """Import msalign"""
    try:
        import msalign

        del msalign

        success = True
    except ImportError:
        success = False

    assert success

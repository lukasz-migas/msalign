"""Test modules importation."""


def test_import_numpy():
    """Import NumPy."""
    import numpy  # noqa


def test_import_scipy():
    """Import scipy."""
    import scipy  # noqa


def test_import_msalign():
    """Import specML"""
    try:
        import msalign  # noqa

        success = True
    except Exception:
        success = False

    assert success

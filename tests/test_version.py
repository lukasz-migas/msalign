from msalign._version import version as __version__


def test_version():
    assert isinstance(__version__, str)

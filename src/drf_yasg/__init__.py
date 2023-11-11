# coding=utf-8
try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

__author__ = """Cristi V."""
__email__ = 'cristi@cvjd.me'

try:
    __version__ = importlib_metadata.version(__name__)
except importlib_metadata.PackageNotFoundError:  # pragma: no cover
    # package is not installed
    pass

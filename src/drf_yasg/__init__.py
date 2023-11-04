# coding=utf-8
import importlib.metadata

__author__ = """Cristi V."""
__email__ = 'cristi@cvjd.me'

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    # package is not installed
    pass

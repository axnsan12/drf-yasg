# coding=utf-8
from importlib.metadata import version, PackageNotFoundError

__author__ = """Cristi V."""
__email__ = 'cristi@cvjd.me'

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass

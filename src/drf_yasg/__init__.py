# coding=utf-8
from pkg_resources import get_distribution, DistributionNotFound

__author__ = """Cristi V."""
__email__ = 'cristi@cvjd.me'

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    pass

#!/usr/bin/env python
from setuptools import setup

try:
    # noinspection PyUnresolvedReferences
    import setuptools_scm  # noqa: F401

    setup(use_scm_version=True)
except (ImportError, LookupError) as e:
    import os
    import sys

    if os.getenv("CI", "false") == "true":
        # don't silently fail on CI - we don't want to accidentally push a dummy version
        # to PyPI
        raise

    err_msg = str(e)
    if "setuptools-scm" in err_msg or "setuptools_scm" in err_msg:
        import time
        import traceback

        timestamp_ms = int(time.time() * 1000)
        timestamp_str = hex(timestamp_ms)[2:].zfill(16)
        dummy_version = "1!0.0.0.dev0+noscm." + timestamp_str

        setup(version=dummy_version)

        traceback.print_exc(file=sys.stderr)
        print(
            "failed to detect version, package was built with dummy version "
            + dummy_version,
            file=sys.stderr,
        )
    else:
        raise

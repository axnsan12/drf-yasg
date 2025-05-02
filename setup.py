#!/usr/bin/env python
import os
import sys

from setuptools import setup


def read_req(req_file):
    with open(os.path.join("requirements", req_file)) as req:
        return [
            line.strip()
            for line in req.readlines()
            if line.strip() and not line.strip().startswith("#")
        ]


requirements = read_req("base.txt")
requirements_validation = read_req("validation.txt")


def drf_yasg_setup(**kwargs):
    setup(
        install_requires=requirements,
        extras_require={
            "validation": requirements_validation,
            "coreapi": ["coreapi>=2.3.3", "coreschema>=0.0.4"],
        },
        **kwargs,
    )


try:
    # noinspection PyUnresolvedReferences
    import setuptools_scm  # noqa: F401

    drf_yasg_setup(use_scm_version=True)
except (ImportError, LookupError) as e:
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

        drf_yasg_setup(version=dummy_version)

        traceback.print_exc(file=sys.stderr)
        print(
            "failed to detect version, package was built with dummy version "
            + dummy_version,
            file=sys.stderr,
        )
    else:
        raise

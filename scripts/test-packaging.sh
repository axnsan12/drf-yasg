#!/bin/sh
set -ev

python setup.py sdist
pip install ./dist/drf_yasg2* --force-reinstall
tox -e py38-django_latest-drf_latest

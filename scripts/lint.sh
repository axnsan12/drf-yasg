#!/bin/sh
set -ev

flake8 src/drf_yasg2 testproj tests setup.py --count

#!/bin/sh
set -ev

sphinx-build -nEa -b html docs docs/_build/html

#!/bin/sh
set -ev
ENVLIST=$(tox -a | grep $1 | xargs | tr " " "," | cat)
tox -e $ENVLIST

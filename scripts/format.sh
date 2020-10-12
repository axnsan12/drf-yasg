#!/bin/sh
set -ev

# Separate imports and let autoflake filter them
isort --apply -sl
autoflake . -ri --exclude 'venv, conftest.py' --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports

# Sort and format
isort --apply
black .

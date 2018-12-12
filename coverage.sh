#!/usr/bin/env bash
set -e

coverage combine || true
coverage report
codecov

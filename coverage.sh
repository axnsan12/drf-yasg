#!/usr/bin/env bash
set -ex

coverage combine
coverage report
codecov

#!/usr/bin/env bash

set -e
set -u

flake8 iapetus && pytest

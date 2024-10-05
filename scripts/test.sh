#!/usr/bin/env bash

set -e
set -x

uv pip compile pyproject.toml -o requirements.txt
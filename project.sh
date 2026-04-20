#!/bin/bash
set -e

export PIP_CACHE_DIR=$PWD/pip_cache
python3 -m pip install --no-cache-dir pandas

FILE=$1
python3 compute_mean.py "$FILE"

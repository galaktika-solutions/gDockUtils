#!/bin/bash
set -e

python /src/gdockutils/gprun.py -u 1000:1000 pip install -e .
exec "$@"

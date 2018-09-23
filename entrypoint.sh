#!/bin/bash
set -e

pip install -e /src &> /dev/null
exec "$@"
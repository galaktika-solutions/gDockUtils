#!/bin/bash
set -e

pip install -e .

if [ "$1" = 'postgres' ]; then
  ensure_db
  exec gprun -u postgres postgres
fi

exec "$@"

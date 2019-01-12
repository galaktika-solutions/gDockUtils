#!/bin/bash
set -e

pip install -e .

if [ "$1" = 'postgres' ]; then
  ensure_db
  exec gprun -u postgres postgres
fi

if [ "$1" = 'distribute' ]; then
  rm -rf dist
  python setup.py sdist
  TWINE_USERNAME="$(readsecret TWINE_USERNAME)" \
  TWINE_PASSWORD="$(readsecret TWINE_PASSWORD)" \
  twine upload dist/*
  exit 0
fi

if [ "$1" = 'sleep' ]; then
  exec gprun -u "$(stat -c %u:%g .)" -s SIGINT sleep 1000
fi

exec "$@"

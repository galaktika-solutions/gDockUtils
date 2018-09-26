#!/bin/bash
set -e

if [ "$1" = 'install' ]; then
  pip install -e /src &> /dev/null
  exit
elif [ "$1" = 'test' ]; then
  su-exec "$(stat -c %u:%g .)" bash \
    -c "coverage run --source gdockutils -m unittest && \
        coverage report && \
        coverage html"
  exit
elif [ "$1" = 'docs' ]; then
  su-exec "$(stat -c %u:%g .)" sphinx-build -b html docs/source docs/build
  exit
elif [ "$1" = 'sdist' ]; then
  python setup.py sdist
  exit
fi

exec "$@"

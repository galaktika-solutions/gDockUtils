#!/usr/bin/env python3

import os
import argparse

import yaml

from .secret import readsecret
from . import SECRET_CONF_FILE, SECRET_DIR


def defined_secrets():
    with open(SECRET_CONF_FILE, 'r') as f:
        doc = yaml.load(f)
    return sorted(doc)


def prepare(service, wait=False):
    os.makedirs(SECRET_DIR, exist_ok=True)
    with open(SECRET_CONF_FILE, 'r') as f:
        doc = yaml.load(f)
    for secret, _services in doc.items():
        if _services and service in _services:
            readsecret(
                secret,
                store='%s:%s:%s:400' % (secret, service, service),
                secret_dir=SECRET_DIR
            )
    if wait:
        from .db import wait_for_db
        wait_for_db()


def prepare_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Mounts secrets (as files) to /run/secrets based on '
            'the settings in conf/secrets.yml'
        ),
    )
    parser.add_argument(
        '-w', '--wait',
        help='wait for the database to start', action="store_true"
    )
    parser.add_argument(
        'service',
        help='the service to prepare'
    )
    args = parser.parse_args()
    prepare(args.service, args.wait)

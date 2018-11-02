#!/usr/bin/env python3

import os

import yaml

from .secret import readsecret
from . import SECRET_CONF_FILE, SECRET_DIR


def defined_secrets():
    with open(SECRET_CONF_FILE, 'r') as f:
        doc = yaml.load(f)
    return sorted(doc)


def prepare(service, wait=False, dev=False):
    os.makedirs(SECRET_DIR, exist_ok=True)
    with open(SECRET_CONF_FILE, 'r') as f:
        doc = yaml.load(f)
    mode = '444' if dev and os.environ.get('ENV') == 'DEV' else '400'
    for secret, _services in doc.items():
        if _services and service in _services:
            readsecret(
                secret,
                store=':'.join([secret, service, service, mode]),
                secret_dir=SECRET_DIR
            )
    if wait:
        from .db import wait_for_db
        wait_for_db()

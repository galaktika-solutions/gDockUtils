#!/usr/bin/env python3

import os

import yaml

from .secret import readsecret
from .db import set_files_perms, wait_for_db


SECRET_CONF_FILE = '/src/conf/secrets.yml'


def prepare_django_main():
    prepare_django()


def prepare(service, secret_conf_file, secret_db_file=None):
    os.makedirs('/run/secrets', exist_ok=True)
    with open(secret_conf_file, 'r') as f:
        doc = yaml.load(f)
    for secret, _services in doc.items():
        for _service, filedef in _services.items():
            if _service == service:
                readsecret(secret, database=secret_db_file, store=filedef)


def prepare_django():
    prepare('django', SECRET_CONF_FILE)
    os.makedirs('/data/files')
    os.makedirs('/data/latex')
    set_files_perms()
    wait_for_db()

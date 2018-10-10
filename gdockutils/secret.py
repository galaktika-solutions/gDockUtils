#!/usr/bin/env python3

import argparse
import sys
import os
import base64
import random as rnd
import string

from . import (
    printerr, AlreadyExists, SecretDatabaseNotFound, DoesNotExist,
    uid, gid
)


SECRET_DATABASE_FILE = '.secret.env'


def existing():
    with open(SECRET_DATABASE_FILE, 'r') as db:
        secretlines = db.readlines()
    secrets = [l.split('=', 1) for l in secretlines if l]
    return sorted(dict([(k, v.strip()) for [k, v] in secrets]))


def readpart(lst, idx, default=None):
    try:
        ret = lst[idx]
    except IndexError:
        ret = None

    if not ret:
        if default is None:
            raise
        return default

    return ret


def createsecret_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Creates a secret in the secret database (./.secret.env).'
        ),
    )
    parser.add_argument(
        '--force',
        help='create the secret even if it already exists',
        action='store_true'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-f', '--fromfile',
        help='read the value from this file'
    )
    group.add_argument(
        '-r', '--random', type=int,
        help='create a random string of the given length'
    )
    group.add_argument(
        '-v', '--value',
        help='use the given value'
    )
    parser.add_argument(
        'secret',
        help='the name of the secret'
    )
    args = parser.parse_args()
    try:
        createsecret(
            args.secret,
            args.fromfile, args.random, args.value, args.force
        )
    except (AlreadyExists, SecretDatabaseNotFound) as e:
        printerr(e.args[0])
        sys.exit(1)


def readsecret_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Reads the given secret from the secret database (./.secret.env).'
        ),
    )
    parser.add_argument(
        '-s', '--store',
        help='store the secret in this file (filename:uid:gid:mode)'
    )
    parser.add_argument(
        'secret',
        help='the name of the secret'
    )
    args = parser.parse_args()
    try:
        ret = readsecret(args.secret, args.store)
    except (DoesNotExist, SecretDatabaseNotFound) as e:
        printerr(e.args[0])
        sys.exit(1)
    sys.stdout.buffer.write(ret)


def createsecret(
        secret, fromfile=None,
        random=None, value=None, force=None,
):
    try:
        readsecret(secret)
    except DoesNotExist:
        pass
    else:
        if not force:
            raise AlreadyExists('Secret %s already exists.' % secret)

    with open(SECRET_DATABASE_FILE, 'r') as db:
        secretlines = db.readlines()
    secrets = [l.split('=', 1) for l in secretlines if l]
    secrets = dict([(k, v.strip()) for [k, v] in secrets])

    if fromfile is not None:
        with open(fromfile, 'rb') as f:
            val = f.read()
    elif value is not None:
        val = value.encode()
    elif random is not None:
        val = ''.join(
            rnd.choice(
                string.ascii_letters + string.digits + string.punctuation
            ) for _ in range(random)
        ).encode()

    secrets[secret] = base64.b64encode(val).decode()

    with open(SECRET_DATABASE_FILE, 'w') as f:
        for k, v in secrets.items():
            f.write('%s=%s\n' % (k, v))


def readsecret(
    secret, store=None, decode=False, secret_dir=''
):
    try:
        with open(SECRET_DATABASE_FILE, 'r') as db:
            secretlines = db.readlines()
    except FileNotFoundError:
        raise SecretDatabaseNotFound(
            'Secret database %s does not exist.' % SECRET_DATABASE_FILE
        )

    value = None
    for secretdef in secretlines:
        if not secretdef:
            continue
        [s, v] = secretdef.split('=', 1)
        if s == secret:
            value = base64.b64decode(v.strip())
            break

    if value is None:
        raise DoesNotExist('Secret %s not found.' % secret)

    if not store:
        return value if not decode else value.decode()

    stat = os.stat('.')
    default_uid, default_gid = stat.st_uid, stat.st_gid
    parts = store.split(':')
    fn = os.path.join(secret_dir, readpart(parts, 0))
    _uid = uid(readpart(parts, 1, default_uid))
    _gid = gid(readpart(parts, 2, default_gid))
    mode = int(readpart(parts, 3, '600'), 8)

    with open(fn, 'wb') as f:
        f.write(value)

    os.chown(fn, _uid, _gid)
    os.chmod(fn, mode)
    return b''

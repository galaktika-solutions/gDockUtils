#!/usr/bin/env python3

import argparse
from . import get_param, uid, gid
from . import printerr, run
import os
# import sys
import time
# from .secret import readsecret


def escape_pwd(pwd):
    pwd = pwd.replace("\\", "\\\\").replace("'", "\\'")
    return "'%s'" % pwd


def conninfo(**kwargs):
    params = (
        'host', 'port', 'user', 'password', 'dbname', 'sslmode', 'sslcert',
        'sslkey', 'sslrootcert'
    )
    ci = dict([(p, kwargs.pop(p, '')) for p in params])
    if ci['password']:
        ci['password'] = escape_pwd(ci['password'])
    return ' '.join(['%s=%s' % (k, v) for k, v in ci.items() if v])


def set_backup_perms(backup_dir=None, backup_uid=None, backup_gid=None):
    default_uid = os.stat('.').st_uid
    backup_dir = get_param(backup_dir, 'BACKUP_DIR', '/backup')
    backup_uid = uid(get_param(backup_uid, 'BACKUP_UID', default_uid))
    backup_gid = gid(get_param(backup_gid, 'BACKUP_GID', backup_uid))

    os.makedirs(os.path.join(backup_dir, 'db'), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'files'), exist_ok=True)

    for root, dirs, files in os.walk(backup_dir):
        os.chown(root, backup_uid, backup_gid)
        os.chmod(root, 0o700)
        for f in files:
            path = os.path.join(root, f)
            os.chown(path, backup_uid, backup_gid)
            os.chmod(path, 0o600)
    os.chmod(backup_dir, 0o755)


def wait_for_db(connstr=None):
    connstr = get_param(connstr, 'CONNSTR', '')
    sql = 'select 1'
    while True:
        try:
            run(['psql', connstr, '-c', sql])
        except Exception:
            printerr('db not ready yet')
            time.sleep(1)
        else:
            printerr('db ready')
            break


def backup_main():
    parser = argparse.ArgumentParser(
        description=(
            'Creates a backup to the /backup directory'
        ),
    )
    parser.add_argument(
        '-d', '--database_format',
        help='creates a database backup to /backup/db using the given format'
             ' (custom or plain)',
        choices=['custom', 'plain']
    )
    parser.add_argument(
        '-f', '--files',
        help='backs up files from /data/files/ to /backup/files',
        action='store_true'
    )
    parser.add_argument(
        '--hostname',
        help=(
            'db backup file names are prefixed with this name '
            '(env: HOST_NAME)'
        )
    )
    parser.add_argument(
        '--connstr',
        help='database connection string (env: CONNSTR)',
    )
    args = parser.parse_args()

    backup(args.database_format, args.files, args.hostname, args.connstr)


def backup(database_format=None, files=None, hostname=None, connstr=None):
    connstr = get_param(connstr, 'CONNSTR', '')
    set_backup_perms()
    wait_for_db(connstr)

    if database_format:
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
        hostname = get_param(hostname, 'HOST_NAME', 'localhost')
        filename = '{hostname}-db-{timestamp}.backup'
        filename = filename.format(hostname=hostname, timestamp=timestamp)
        if database_format == 'plain':
            filename += '.sql'

        run(['pg_dump', '-v', '-F', database_format, '-f', filename, connstr])
        # host=postgres user=django dbname=mv2
        # sslmode=require sslcert=/root/postgresql.crt
        # sslkey=/root/postgresql.key password='escapedstuff'

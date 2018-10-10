#!/usr/bin/env python3

import argparse
import os
import time
from hashlib import md5 as _md5

from . import get_param, uid, gid, printerr, run, cp
from .prepare import prepare
from .secret import readsecret
from .gprun import gprun


# assumptions on the project structure
BACKUP_DIR = 'backup'
DATA_FILES_DIR = '/data/files'
BACKUP_FILE_PREFIX = os.environ.get('HOST_NAME', 'localhost')
PG_HBA_ORIG = 'conf/pg_hba.conf'
POSTGRESCONF_ORIG = 'conf/postgresql.conf'


def md5(s):
    return _md5(s.encode()).hexdigest()


def ensure_db_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Creates database objects and sets up passwords'
        ),
    )
    parser.add_argument(
        'database',
        help='the database to create',
    )
    args = parser.parse_args()

    ensure_db(args.database)


def ensure_db(db):
    """
    Initialize the database, set up users and passwords
    """
    PGDATA = os.environ.get('PGDATA')
    os.makedirs(PGDATA, exist_ok=True)
    os.chmod(PGDATA, 0o700)
    u, g = uid('postgres'), gid('postgres')
    for root, dirs, files in os.walk(PGDATA):
        os.chown(root, u, g)

    PG_VERSION = os.path.join(PGDATA, 'PG_VERSION')
    if not os.path.isfile(PG_VERSION) or os.path.getsize(PG_VERSION) == 0:
        gprun(userspec='postgres', command=['initdb'], sys_exit=False)

    dest = os.path.join(PGDATA, 'pg_hba.conf')
    cp(PG_HBA_ORIG, dest, 'postgres', 'postgres', 0o600)

    dest = os.path.join(PGDATA, 'postgresql.conf')
    cp(POSTGRESCONF_ORIG, dest, 'postgres', 'postgres', 0o600)

    prepare('postgres')

    dbpass = readsecret('DB_PASSWORD', decode=True)
    dbpass_postgres = "'md5%s'" % md5(dbpass + 'postgres')
    dbpass_django = "'md5%s'" % md5(dbpass + 'django')
    dbpass_explorer = "'md5%s'" % md5(dbpass + 'explorer')

    # start postgres locally
    gprun(userspec='postgres', sys_exit=False, command=[
        'pg_ctl',
        '-o', "-c listen_addresses='127.0.0.1'",
        '-o', "-c log_statement=none",
        '-o', "-c log_connections=off",
        '-o', "-c log_disconnections=off",
        '-w', 'start'
    ])

    run([
        'psql', '-h', '127.0.0.1', '-U', 'postgres',
        '-c', 'ALTER ROLE postgres ENCRYPTED PASSWORD %s' % dbpass_postgres,
        '-c', 'CREATE ROLE django',
        '-c', 'ALTER ROLE django '
              'ENCRYPTED PASSWORD %s LOGIN SUPERUSER' % dbpass_django,
        '-c', 'CREATE ROLE explorer',
        '-c', 'ALTER ROLE explorer '
              'ENCRYPTED PASSWORD %s LOGIN' % dbpass_explorer,
        '-c', '\c postgres django',
        '-c', 'CREATE DATABASE %s' % db,
        '-c', '\c %s django' % db,
        '-c', 'REVOKE CREATE ON SCHEMA public FROM public',
        '-c', 'GRANT SELECT ON ALL TABLES IN SCHEMA public TO explorer',
        '-c', 'ALTER DEFAULT PRIVILEGES FOR USER django IN SCHEMA public '
              'GRANT SELECT ON TABLES TO explorer'
    ])

    # stop the internally started postgres
    gprun(userspec='postgres', sys_exit=False, command=[
        'pg_ctl', 'stop', '-s', '-w', '-m', 'fast'
    ])


def set_backup_perms(backup_uid, backup_gid):
    os.makedirs(os.path.join(BACKUP_DIR, 'db'), exist_ok=True)
    os.makedirs(os.path.join(BACKUP_DIR, 'files'), exist_ok=True)

    for root, dirs, files in os.walk(BACKUP_DIR):
        os.chown(root, backup_uid, backup_gid)
        os.chmod(root, 0o700)
        for f in files:
            path = os.path.join(root, f)
            os.chown(path, backup_uid, backup_gid)
            os.chmod(path, 0o600)
    os.chmod(BACKUP_DIR, 0o755)


def set_files_perms():
    os.makedirs(DATA_FILES_DIR, exist_ok=True)
    u, g = uid('django'), gid('nginx')
    for root, dirs, files in os.walk(DATA_FILES_DIR):
        os.chown(root, u, g)
        os.chmod(root, 0o2750)
        for f in files:
            path = os.path.join(root, f)
            os.chown(path, u, g)
            os.chmod(path, 0o640)


def wait_for_db():
    while True:
        try:
            run(['psql', '-c', 'select 1'], silent=True)
        except Exception:
            printerr('db not ready yet')
            time.sleep(1)
        else:
            printerr('db ready')
            break


def backup_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Creates a backup to the /backup directory'
        ),
    )
    parser.add_argument(
        '-d', '--database_format',
        help='Creates a database backup to BACKUP_DIR/db using the given '
             'format (custom or plain).',
        choices=['custom', 'plain']
    )
    parser.add_argument(
        '-f', '--files',
        help='backs up files from /data/files/ to BACKUP_DIR/files',
        action='store_true'
    )
    parser.add_argument(
        '--backup_uid',
        help='the uid of the backup user',
    )
    parser.add_argument(
        '--backup_gid',
        help='the gid of the backup user',
    )
    args = parser.parse_args()

    backup(
        args.database_format, args.files,
        args.backup_uid, args.backup_gid
    )


def restore_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Restores database and files.'
        ),
    )
    parser.add_argument(
        '-f', '--db_backup_file',
        help='the database backup filename (not the path)'
    )
    parser.add_argument(
        '--files',
        help='restore files also (flag)',
        action='store_true'
    )
    parser.add_argument(
        '--drop_db',
        help='the database to drop',
    )
    parser.add_argument(
        '--create_db',
        help='the database to create',
    )
    parser.add_argument(
        '--owner',
        help='the owner of the created database',
    )
    args = parser.parse_args()

    restore(
        args.db_backup_file, args.files,
        args.drop_db, args.create_db, args.owner
    )


def backup(
    database_format=None, files=None,
    backup_uid=None, backup_gid=None
):
    default_uid = os.stat('.').st_uid
    backup_uid = uid(get_param(backup_uid, 'BACKUP_UID', default_uid))
    backup_gid = gid(get_param(backup_gid, 'BACKUP_GID', backup_uid))

    if database_format:
        wait_for_db()
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
        filename = '{prefix}-db-{timestamp}.backup'
        filename = filename.format(
            prefix=BACKUP_FILE_PREFIX, timestamp=timestamp
        )
        if database_format == 'plain':
            filename += '.sql'
        filename = os.path.join(BACKUP_DIR, 'db', filename)

        cmd = ['pg_dump', '-v', '-F', database_format, '-f', filename]
        run(cmd, log_command=True)

    if files:
        cmd = [
            'rsync', '-v', '-a', '--delete', '--stats',
            DATA_FILES_DIR, os.path.join(BACKUP_DIR, 'files/')
        ]
        run(cmd, log_command=True)

    set_backup_perms(backup_uid, backup_gid)


def restore(
    db_backup_file=None, files=None,
    drop_db=None, create_db=None, owner=None
):
    if db_backup_file:
        wait_for_db()
        db_backup_file = os.path.join(BACKUP_DIR, 'db', db_backup_file)
        if db_backup_file.endswith('.backup'):
            # -h postgres -U postgres -d postgres
            cmd = [
                'pg_restore', '--exit-on-error', '--verbose',
                '--clean', '--create', db_backup_file
            ]
            run(cmd, log_command=True)
        elif db_backup_file.endswith('.backup.sql'):
            drop_db = get_param(drop_db, 'DROP_DB', 'django')
            create_db = get_param(create_db, 'CREATE_DB', drop_db)
            owner = get_param(owner, 'OWNER', 'django')
            run([
                'psql', '-U', 'postgres', '-d', 'postgres',
                '-c', 'DROP DATABASE %s' % drop_db,
                '-c', 'CREATE DATABASE %s OWNER %s' % (create_db, owner)
            ])
            run([
                'psql', '-v', 'ON_ERROR_STOP=1', '-U', owner, '-d', create_db,
                '-f', db_backup_file
            ])

    if files:
        cmd = [
            'rsync', '-v', '-a', '--delete', '--stats',
            os.path.join(BACKUP_DIR, 'files/'), DATA_FILES_DIR
        ]
        run(cmd, log_command=True)
        set_files_perms()

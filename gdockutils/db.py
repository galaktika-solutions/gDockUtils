#!/usr/bin/env python3

import argparse
from . import get_param, uid, gid
from . import printerr, run
import os
import time


# assumptions on the project structure
BACKUP_DIR = '/backup'
DATA_FILES_DIR = '/data/files'
BACKUP_FILE_PREFIX = os.environ.get('HOST_NAME', 'localhost')


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
    u, g = uid('django'), gid('nginx')
    for root, dirs, files in os.walk(DATA_FILES_DIR):
        os.chown(root, u, g)
        os.chmod(root, 0o2750)
        for f in files:
            path = os.path.join(root, f)
            os.chown(path, u, g)
            os.chmod(path, 0o640)
    os.chown('/data/latex', u, u)


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

    wait_for_db()

    if database_format:
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

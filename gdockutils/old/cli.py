import argparse
import sys

from .db import ensure_db as _ensure_db
from .db import backup as _backup
from .db import restore as _restore
from . import DATABASE_NAME, DATABASE_USER
from .secret import createsecret as _createsecret
from .secret import readsecret as _readsecret
from . import SecretAlreadyExists, SecretDatabaseNotFound, SecretDoesNotExist
from . import printerr
from .prepare import prepare as _prepare


def ensure_db():
    parser = argparse.ArgumentParser(
        description=("Creates database objects and sets up passwords")
    )
    parser.add_argument(
        "-d", "--database", help="the database to create", default=DATABASE_NAME
    )
    parser.add_argument("-u", "--user", help="the database user", default=DATABASE_USER)
    args = parser.parse_args()

    _ensure_db(args.database, args.user)


def backup():
    parser = argparse.ArgumentParser(
        description=("Creates a backup to the /backup directory")
    )
    parser.add_argument(
        "-d",
        "--database_format",
        help="Creates a database backup to BACKUP_DIR/db using the given "
        "format (custom or plain).",
        choices=["custom", "plain"],
    )
    parser.add_argument(
        "-f",
        "--files",
        help="backs up files from /data/files/ to BACKUP_DIR/files",
        action="store_true",
    )
    parser.add_argument("--backup_uid", help="the uid of the backup user")
    parser.add_argument("--backup_gid", help="the gid of the backup user")
    args = parser.parse_args()

    _backup(args.database_format, args.files, args.backup_uid, args.backup_gid)


def restore():
    parser = argparse.ArgumentParser(description=("Restores database and files."))
    parser.add_argument(
        "-f", "--db_backup_file", help="the database backup filename (not the path)"
    )
    parser.add_argument(
        "--files", help="restore files also (flag)", action="store_true"
    )
    parser.add_argument("--drop_db", help="the database to drop", default=DATABASE_NAME)
    parser.add_argument(
        "--create_db", help="the database to create", default=DATABASE_NAME
    )
    parser.add_argument(
        "--owner", help="the owner of the created database", default=DATABASE_USER
    )
    args = parser.parse_args()

    _restore(args.db_backup_file, args.files, args.drop_db, args.create_db, args.owner)


def createsecret():
    parser = argparse.ArgumentParser(
        description=("Creates a secret in the secret database (./.secret.env).")
    )
    parser.add_argument(
        "--force",
        help="create the secret even if it already exists",
        action="store_true",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--fromfile", help="read the value from this file")
    group.add_argument(
        "-r", "--random", type=int, help="create a random string of the given length"
    )
    group.add_argument("-v", "--value", help="use the given value")
    parser.add_argument("secret", help="the name of the secret")
    args = parser.parse_args()
    try:
        _createsecret(args.secret, args.fromfile, args.random, args.value, args.force)
    except (SecretAlreadyExists, SecretDatabaseNotFound) as e:
        printerr(e.args[0])
        sys.exit(1)


def readsecret():
    parser = argparse.ArgumentParser(
        description=("Reads the given secret from the secret database (./.secret.env).")
    )
    parser.add_argument(
        "-s", "--store", help="store the secret in this file (filename:uid:gid:mode)"
    )
    parser.add_argument("secret", help="the name of the secret")
    args = parser.parse_args()
    try:
        ret = _readsecret(args.secret, args.store)
    except (SecretDoesNotExist, SecretDatabaseNotFound) as e:
        printerr(e.args[0])
        sys.exit(1)
    sys.stdout.buffer.write(ret)


def prepare():
    parser = argparse.ArgumentParser(
        description=(
            "Mounts secrets (as files) to /run/secrets based on "
            "the settings in conf/secrets.yml"
        )
    )
    parser.add_argument(
        "-w", "--wait", help="wait for the database to start", action="store_true"
    )
    parser.add_argument(
        "-u", "--user", help="secrets will be owned by the given user:group"
    )
    parser.add_argument("service", help="the service to prepare")
    args = parser.parse_args()

    _prepare(args.service, args.wait, args.user)

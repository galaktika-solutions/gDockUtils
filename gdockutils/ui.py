#!/usr/bin/env python3

import argparse
import sys
import os

from . import printerr, NoChoiceError
from .db import BACKUP_DIR, restore, backup
from .secret import (
    SECRET_DATABASE_FILE, readsecret, DoesNotExist, createsecret, existing
)
from .prepare import defined_secrets


SECRET_SOURCE_DIR = '.files'


def ask_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Asks the user to select one (or more) from a list of options.'
        ),
    )
    parser.add_argument(
        '-p', '--prompt',
        default='Select an option:',
        help=(
            'print a description to the user'
        )
    )
    parser.add_argument(
        '-d', '--default',
        help=(
            'the default selection to use'
        )
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-m', '--multiple',
        help='multiple choice',
        action='store_true'
    )
    group.add_argument(
        '-y', '--yesno',
        help='yes/no question',
        action='store_true'
    )
    parser.add_argument(
        'options',
        help=(
            'the options to choose from'
        ),
        nargs='*'
    )
    args = parser.parse_args()
    if not args.options and not args.yesno:
        parser.error('Options can only be empty in case of a yes/no question.')
    if args.yesno and args.default and args.default not in ('y', 'n'):
        parser.error(
            'In case of a yes/no question, default must be "y" or "n"'
        )

    try:
        ret = ask(
            options=args.options, prompt=args.prompt,
            default=args.default, multiple=args.multiple,
            yesno=args.yesno
        )
    except NoChoiceError as e:
        printerr(e.args[0])
        sys.exit(1)
    if args.multiple:
        [print(r) for r in ret]
    else:
        print(ret)


def ask(options=[], prompt='', default=None, multiple=False, yesno=False):
    """
    Asks the user to select one (or more) from a list of options.

    Example::

        from gdockutils.ui import ask

        ask(prompt='Are you sure?', yesno=True, default='n')
    """

    if yesno:
        if default == 'y':
            msg = 'Y/n'
        elif default == 'n':
            msg = 'y/N'
        else:
            msg = 'y/n'
        while True:
            printerr('%s [%s]: ' % (prompt, msg), end='')
            i = input()
            if not i and default:
                return True if default == 'y' else False
            if not i:
                continue
            if i[0] in 'Yy':
                return True
            if i[0] in 'Nn':
                return False

    if not options:
        raise NoChoiceError('Nothing to choose from.')
    options = [o if isinstance(o, tuple) else (o, o) for o in options]
    if prompt:
        printerr('\n%s\n' % prompt)
    else:
        printerr('')
    for i, o in enumerate(options):
        d = '*' if o[0] == default else ' '
        printerr('{:>3} {} {}'.format(i, d, o[1]))
    printerr('')

    while True:
        if multiple:
            msg = 'Enter selected numbers in range 0-{}, separated by commas: '
        else:
            msg = 'Enter a number in range 0-{}: '
        printerr(msg.format(len(options) - 1), end='')

        i = input()
        if not i and default:
            return default
        try:
            if multiple:
                return set([options[int(x)][0] for x in i.split(',')])
            return options[int(i)][0]
        except (ValueError, IndexError):
            continue


def backup_ui():
    parser = argparse.ArgumentParser(
        description=(
            'Perform a backup by asking the user for parameters.'
        ),
    )
    parser.add_argument(
        '-d', '--database',
        help='offer database type backup',
        action='store_true'
    )
    parser.add_argument(
        '-f', '--files',
        help='offer "files" type backup',
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

    types = []
    if args.database:
        types.append('database')
    if args.files:
        types.append('files')
    if len(types) == 0:
        parser.error('No backup type given.')
    if len(types) == 1:
        typ = types[0]
    else:
        typ = ask(
            types,
            prompt='What would you like to backup?',
            multiple=True
        )

    database_format = None
    if args.database:
        database_format = ask(
            ['custom', 'plain'],
            prompt='Which db backup format do you want to use?'
        )

    backup(
        database_format, 'files' in typ,
        args.backup_uid, args.backup_gid
    )


def restore_ui():
    parser = argparse.ArgumentParser(
        description=(
            'Perform a restore by asking the user for parameters.'
        ),
    )
    parser.add_argument(
        '-d', '--database',
        help='offer database type restore',
        action='store_true'
    )
    parser.add_argument(
        '-f', '--files',
        help='offer "files" type restore',
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

    types = []
    if args.database:
        types.append('database')
    if args.files:
        types.append('files')
    if len(types) == 0:
        parser.error('No restore type given.')
    if len(types) == 1:
        typ = types[0]
    else:
        typ = ask(
            types,
            prompt='What would you like to restore?',
            multiple=True
        )

    db_backup_file = None
    if 'database' in typ:
        db_backup_dir = os.path.join(BACKUP_DIR, 'db')
        entries = os.listdir(db_backup_dir)
        entries = sorted([
            e
            for e in entries
            if os.path.isfile(os.path.join(db_backup_dir, e))
        ])
        db_backup_file = ask(
            entries, prompt='Which db backup file would you like to use?'
        )

    restore(
        db_backup_file, 'files' in typ,
        args.drop_db, args.create_db, args.owner
    )


def createsecret_ui():
    if not os.path.isfile(SECRET_DATABASE_FILE):
        with open(SECRET_DATABASE_FILE, 'w'):
            pass
        os.chmod(SECRET_DATABASE_FILE, 0o600)
    secret = ask(
        defined_secrets(),
        prompt='Which secret would you like to create?'
    )
    try:
        readsecret(secret)
    except DoesNotExist:
        pass
    else:
        if not ask(
            prompt='The secret already exists. Would you like to recreate it?',
            yesno=True, default='n'
        ):
            return

    modes = [
        ('r', 'create a random string'),
        ('v', 'type it in the terminal')
    ]

    entries = []
    if os.path.isdir(SECRET_SOURCE_DIR):
        entries = os.listdir(SECRET_SOURCE_DIR)
        entries = sorted([
            e
            for e in entries
            if os.path.isfile(os.path.join(SECRET_SOURCE_DIR, e))
        ])
        if entries:
            msg = 'encode a file in the %s folder' % SECRET_SOURCE_DIR
            modes.insert(0, ('f', msg))
    mode = ask(modes, prompt='How would you like to create the secret?')
    if mode == 'f':
        source_file = ask(entries, 'Select the file')
        source_file = os.path.join(SECRET_SOURCE_DIR, source_file)
        createsecret(secret, fromfile=source_file, force=True)
    elif mode == 'r':
        while True:
            printerr('Enter the length of the string (1-999)', end=': ')
            i = input()
            try:
                i = int(i)
                if i > 0 and i < 1000:
                    break
            except ValueError:
                continue
        createsecret(secret, random=i, force=True)
    else:
        printerr('Enter the secret value', end=': ')
        createsecret(secret, value=input(), force=True)


def readsecret_ui():
    secrets = existing()
    if not secrets:
        return
    secret = ask(
        secrets,
        prompt='Select a secret'
    )
    sys.stdout.buffer.write(readsecret(secret))

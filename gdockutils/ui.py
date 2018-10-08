#!/usr/bin/env python3

import argparse

from . import printerr


def ask_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Asks the user to select one from a list of options.'
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
    parser.add_argument(
        'options',
        help=(
            'the options to choose from'
        ),
        nargs='+'
    )
    args = parser.parse_args()

    print(ask(
        options=args.options, prompt=args.prompt, default=args.default
    ), end='')


def ask(options=[], prompt='', default=None):
    if not options:
        printerr('Nothing to choose from.')
    if prompt:
        printerr('\n%s\n' % prompt)
    else:
        printerr('')
    for i, o in enumerate(options):
        d = '*' if o == default else ' '
        printerr('{:>3} {} {}'.format(i, d, o))
    printerr('')
    while True:
        printerr(
            'Enter a number in range 0-{}: '.format(len(options) - 1),
            end=''
        )
        i = input()
        if not i and default:
            return default
        try:
            return options[int(i)]
        except Exception:
            continue

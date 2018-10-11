#!/usr/bin/env python3

import argparse
import pwd
import grp
import os
import subprocess
import signal
import sys


def get_userspec(spec):
    if spec is None:
        return None, None, None, None, None
    _spec = spec.split(':')
    if len(_spec) > 2:
        raise Exception('wrong userspec: %r' % spec)

    uspec = _spec[0]
    if len(_spec) == 1:
        gspec = None
    else:
        gspec = _spec[1]

    try:
        uid = int(uspec)
    except ValueError:
        try:
            pw = pwd.getpwnam(uspec)
        except KeyError:
            raise Exception('user %r does not exist' % uspec)
        else:
            uid, username, homedir = pw.pw_uid, pw.pw_name, pw.pw_dir
    else:
        try:
            pw = pwd.getpwuid(uid)
            username, homedir = pw.pw_name, pw.pw_dir
        except KeyError:
            username, homedir = None, None

    if gspec is None:
        # we try to set additional groups based on the user pwd
        try:
            pw = pwd.getpwuid(uid)
            gid = pw.pw_gid
        except KeyError:
            gid, groups = None, None
        else:
            groups = [
                grp.getgrnam(gr.gr_name).gr_gid
                for gr in grp.getgrall()
                if username in gr.gr_mem
            ]
    else:
        try:
            gid = int(gspec)
        except ValueError:
            try:
                gr = grp.getgrnam(gspec)
            except KeyError:
                raise Exception('group %r does not exist' % gspec)
            else:
                gid = gr.gr_gid
        groups = [gid]

    return uid, username, homedir, gid, groups


def gprun(userspec=None, stopsignal=None, command=[], sys_exit=True):
    """
    Runs the specified command using different user/group. On SIGTERM and
    SIGINT, sends the specified signal to the process.

    :param str userspec: either a user name (``john``) or user name and
      group name separated with colon (``john:postgres``).
      Numeric uid/gid values can be used instead of names.
    :param str stopsignal: the signal to send to the subprocess when a
      ``SIGTERM`` or a ``SIGINT`` received. ex.: ``SIGINT``.
    :param list command: the same as in ``subprocess.run()``.
    :param bool sys_exit: if set to ``False``, the system will not exit when
      the subprocess exits.

    Example::

        from gdockutils.gprun import gprun

        gprun(userspec='postgres', command=['initdb'], sys_exit=False)
    """
    uid, username, homedir, gid, groups = get_userspec(userspec)

    def preexec():
        if groups is not None:
            os.setgroups(groups)
        if gid:
            os.setgid(gid)
        if uid:
            os.setuid(uid)

    env = os.environ.copy()
    if username is not None:
        env['USER'] = username
    if homedir is not None:
        env['HOME'] = homedir
    if uid is not None:
        env['UID'] = str(uid)

    if stopsignal is not None:
        try:
            sig = getattr(signal, stopsignal)
        except AttributeError:
            raise Exception('bad signal: %r' % stopsignal)
    else:
        sig = None

    proc = subprocess.Popen(
        command, preexec_fn=preexec, env=env,
        start_new_session=True
    )

    def handler(signum, frame):
        proc.send_signal(sig if sig is not None else signum)

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    returncode = proc.wait()
    if sys_exit:
        sys.exit(returncode)


def gprun_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Runs the specified command using different user/group.\n'
            'On SIGTERM and SIGINT, sends the specified signal to the process.'
        ),
        usage='gprun [-h] [-u USERSPEC] [-s STOPSIGNAL] command [...]'
    )
    parser.add_argument(
        '-u', '--userspec',
        help=(
            'user/group to switch to in the form '
            '(uid|username)[:(gid|groupname)]'
        )
    )
    parser.add_argument(
        '-s', '--stopsignal',
        help='the name of the signal to send to the process'
    )
    parser.add_argument(
        'command',
        nargs=argparse.REMAINDER,
        # nargs='+',
        help='the command to run'
    )
    args = parser.parse_args()
    if not args.command:
        parser.error('No command given')

    gprun(
        userspec=args.userspec,
        stopsignal=args.stopsignal,
        command=args.command
    )


if __name__ == '__main__':
    gprun_cli()

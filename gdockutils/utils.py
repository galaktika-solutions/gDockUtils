import subprocess
import pwd
import grp

import click


def run(cmd, silent=False, log_command=False, cwd=None, env=None):
    if log_command:
        click.echo(' '.join(cmd), err=True)
    subprocess.run(
        cmd, check=True,
        stdout=subprocess.PIPE if silent else None,
        stderr=subprocess.PIPE if silent else None,
        cwd=cwd, env=env
    )


def uid(spec):
    try:
        return int(spec)
    except ValueError:
        try:
            pw = pwd.getpwnam(spec)
        except KeyError:
            raise Exception('User %r does not exist' % spec)
        else:
            return pw.pw_uid


def gid(spec):
    try:
        return int(spec)
    except ValueError:
        try:
            gr = grp.getgrnam(spec)
        except KeyError:
            raise Exception('Group %r does not exist' % spec)
        else:
            return gr.gr_gid

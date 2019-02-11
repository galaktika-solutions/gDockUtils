import subprocess
import pwd
import grp
import os
from functools import wraps

import click

from .exceptions import ImproperlyConfigured, RootModeNeeded


def run(cmd, silent=False, log_command=False, cwd=None, env=None):
    if log_command:
        click.echo(" ".join(cmd), err=True)
    subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.PIPE if silent else None,
        stderr=subprocess.PIPE if silent else None,
        cwd=cwd,
        env=env,
    )


def uid(spec):
    try:
        return int(spec)
    except ValueError:
        try:
            pw = pwd.getpwnam(spec)
        except KeyError:
            raise Exception("User %r does not exist" % spec)
        else:
            return pw.pw_uid


def gid(spec):
    try:
        return int(spec)
    except ValueError:
        try:
            gr = grp.getgrnam(spec)
        except KeyError:
            raise Exception("Group %r does not exist" % spec)
        else:
            return gr.gr_gid


def path_check(path, uid, gid, mask, root_mode=False, create_file=False):
    if create_file and not os.path.isfile(path):
        if root_mode:
            open(path, "w").close()
        else:
            raise ImproperlyConfigured("No such file: {}".format(path))

    stat = os.stat(path)
    if stat.st_uid != uid:
        if root_mode:
            os.chown(path, uid, gid)
        else:
            msg = "Must be owned by uid {}: {}".format(uid, path)
            raise ImproperlyConfigured(msg)
    if stat.st_mode & mask:
        if root_mode:
            os.chmod(path, stat.st_mode - (stat.st_mode & mask))
        else:
            msg = "Wrong permissions ({:o}): {}".format(stat.st_mode, path)
            raise ImproperlyConfigured(msg)


def root_mode_needed(fnc):
    @wraps(fnc)
    def check_root(self, *args, **kwargs):
        if not self.root_mode:
            raise RootModeNeeded(fnc)
        return fnc(self, *args, **kwargs)

    return check_root

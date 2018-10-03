import sys
import subprocess
import os
import pwd
import grp


def printerr(s, end='\n'):
    print(s, file=sys.stderr, end=end)


def run(cmd):
    subprocess.run(cmd, check=True)


def get_param(var, env_var, default):
    if var is not None:
        return var
    env = os.environ.get(env_var)
    if env is not None:
        return env
    return default


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


class DoesNotExist(Exception):
    pass


class SecretDatabaseNotFound(Exception):
    pass


class AlreadyExists(Exception):
    pass

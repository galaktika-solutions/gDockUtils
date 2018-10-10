import sys
import subprocess
import os
import pwd
import grp
import shutil


def printerr(s, end='\n'):
    print(s, file=sys.stderr, end=end)


def run(cmd, silent=False, log_command=False, cwd=None):
    if log_command:
        printerr(' '.join(cmd))
    subprocess.run(
        cmd, check=True,
        stdout=subprocess.PIPE if silent else None,
        stderr=subprocess.PIPE if silent else None,
        cwd=cwd
    )


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


def cp(source, dest, _uid=-1, _gid=-1, mode=None):
    shutil.copyfile(source, dest)
    os.chown(dest, uid(_uid), gid(_gid))
    os.chmod(dest, mode)


class DoesNotExist(Exception):
    pass


class SecretDatabaseNotFound(Exception):
    pass


class AlreadyExists(Exception):
    pass


class NoChoiceError(Exception):
    pass

import sys
import subprocess
import os
import pwd
import grp
import shutil


def get(env_var, default):
    return os.environ.get(env_var, default)


SECRET_CONF_FILE = get('GDOCKUTILS_SECRET_CONF_FILE', 'conf/secrets.yml')
SECRET_DIR = get('GDOCKUTILS_SECRET_DIR', '/run/secrets')
BACKUP_DIR = get('GDOCKUTILS_BACKUP_DIR', 'backup')
DATA_FILES_DIR = get('GDOCKUTILS_DATA_FILES_DIR', '/data/files')
BACKUP_FILE_PREFIX = get(
    'GDOCKUTILS_BACKUP_FILE_PREFIX',
    get('HOST_NAME', 'localhost')
)
PG_HBA_ORIG = get('GDOCKUTILS_PG_HBA_ORIG', 'conf/pg_hba.conf')
POSTGRESCONF_ORIG = get('GDOCKUTILS_POSTGRESCONF_ORIG', 'conf/postgresql.conf')
SECRET_DATABASE_FILE = get('GDOCKUTILS_SECRET_DATABASE_FILE', '.secret.env')
SECRET_SOURCE_DIR = get('GDOCKUTILS_SECRET_SOURCE_DIR', '.files')
PGDATA = get(
    'GDOCKUTILS_PGDATA',
    get('PGDATA', '/data/postgres')
)
DATABASE_NAME = get('GDOCKUTILS_DATABASE_NAME', 'django')
DATABASE_USER = get('GDOCKUTILS_DATABASE_USER', 'django')
DATABASE_HOST = get('GDOCKUTILS_DATABASE_HOST', 'postgres')
DEBUG = get('GDOCKUTILS_DEBUG', '')


def read_secret_from_file(secret):
    with open(os.path.join(SECRET_DIR, secret)) as f:
        return f.read()


def printerr(s, end='\n'):
    print(s, file=sys.stderr, end=end)


def run(cmd, silent=False, log_command=False, cwd=None, env=None):
    if log_command:
        printerr(' '.join(cmd))
    subprocess.run(
        cmd, check=True,
        stdout=subprocess.PIPE if silent else None,
        stderr=subprocess.PIPE if silent else None,
        cwd=cwd, env=env
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


def parseuidgid(spec):
    spec = spec.split(':')
    u = uid(spec[0])
    if len(spec) == 2:
        return u, gid(spec[1])
    elif len(spec) == 1:
        pw = pwd.getpwuid(u)
        return u, pw.pw_gid


def cp(source, dest, _uid=-1, _gid=-1, mode=None):
    shutil.copyfile(source, dest)
    os.chown(dest, uid(_uid), gid(_gid))
    os.chmod(dest, mode)


class SecretDoesNotExist(Exception):
    pass


class SecretDatabaseNotFound(Exception):
    pass


class SecretAlreadyExists(Exception):
    pass


class NoChoiceError(Exception):
    pass

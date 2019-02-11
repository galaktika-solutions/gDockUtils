import os

from .utils import uid, gid  # cp
from .surun import surun

# from .prepare import prepare


def ensure_db(pgdata="/data/postgres"):
    """Initializes the database, sets up users and passwords.

    The database must not be running, it will be started locally.
    """

    os.makedirs(pgdata, exist_ok=True)
    os.chmod(pgdata, 0o700)
    u, g = uid("postgres"), gid("postgres")
    for root, dirs, files in os.walk(pgdata):
        os.chown(root, u, g)

    PG_VERSION = os.path.join(pgdata, "PG_VERSION")
    if not os.path.isfile(PG_VERSION) or os.path.getsize(PG_VERSION) == 0:
        surun("postgres", command=["initdb"], sys_exit=False)

    # dest = os.path.join(pgdata, "pg_hba.conf")
    # cp(pg_hba_conf_path, dest, "postgres", "postgres", 0o600)
    #
    # dest = os.path.join(pgdata, "postgresql.conf")
    # cp(postgresql_conf_path, dest, "postgres", "postgres", 0o600)
    #
    # # for the database to be able to run the certificates must be in place
    # prepare("postgres")
    #
    # # hba_file=''

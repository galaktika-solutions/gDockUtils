import click

from .createcerts import createcerts as _createcerts
# from .surun import surun as _surun
# from .ensure_db import ensure_db as _ensure_db


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "-n",
    "--name",
    multiple=True,
    required=True,
    envvar="HOST_NAME",
    help="A name the certificate is valid for",
)
@click.option(
    "-i",
    "--ip",
    multiple=True,
    envvar="SERVER_IP",
    default=("127.0.0.1",),
    type=str,
    help="An IP address the certificate is valid for",
)
@click.option(
    "-o",
    "--outputdir",
    envvar="GSTACK_INPUTOUTPUTDIR",
    default="/project/.files",
    type=click.Path(exists=True, file_okay=False),
    help="The directory where the certificates will be created",
)
def createcerts(name, ip, outputdir):
    """Creates certificates for development purposes."""

    _createcerts(name, ip, outputdir)


@cli.command()
def list():
    import sys
    from .conf import Config
    sys.path += ['tests/fixtures']
    config = Config(
        config_module='conf1',
        env_file='tests/conf/.env',
        secret_file='tests/conf/.secret.env',
        root_mode=True,
    )
    config.list()

# @cli.command()
# @click.option(
#     "-u",
#     "--userspec",
#     help="user/group to switch to in the form " "(uid|username)[:(gid|groupname)]",
# )
# @click.option(
#     "-s", "--stopsignal", help="The name of the signal to send to the process"
# )
# @click.argument("command", nargs=-1)
# def surun(userspec, stopsignal, command):
#     """Runs the specified command using different user/group.
#
#     On SIGTERM and SIGINT, sends the specified signal to the process.
#     """
#
#     if not command:
#         raise click.UsageError('No command given.')
#     _surun(userspec, stopsignal, command)
#
#
# @cli.command()
# def ensure_db():
#     """Initializes the database, sets up users and passwords."""
#
#     _ensure_db()

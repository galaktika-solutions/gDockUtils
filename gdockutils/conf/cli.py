import click

from . import Config


@click.group()
@click.pass_context
def conf(ctx):
    """Configuration tools."""
    ctx.obj = Config()


@conf.command()
@click.argument("name")
@click.pass_obj
def get(config, name):
    click.echo(config[name])

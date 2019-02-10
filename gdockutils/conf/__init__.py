import importlib
import os
import inspect

import click

from .exceptions import ImproperlyConfigured, ConfigMissing
from .items import Secret


class Config:
    def __init__(
        self, config_module=None, env_file=None, secret_file=None, secret_dir=None
    ):
        self.config_module = config_module or os.environ.get(
            "GSTACK_CONFIG_MODULE", "gstack_conf"
        )
        self.env_file = env_file or os.environ.get("GSTACK_ENV_FILE", ".env")
        self.secret_file = secret_file or os.environ.get(
            "GSTACK_SECRET_FILE", ".secret.env"
        )
        self.secret_dir = secret_dir or os.environ.get(
            "GSTACK_SECRET_DIR", "/run/secrets"
        )

        mod = importlib.import_module(self.config_module)
        self.items = {}
        classes = [
            c[1] for c in inspect.getmembers(mod) if hasattr(c[1], "_gdockutils_order")
        ]
        classes.sort(key=lambda x: x._gdockutils_order)
        for conf_cls in classes:
            for name in conf_cls.names:
                if name in self.items:
                    raise ImproperlyConfigured(
                        "The config name {} was defined "
                        "multiple times (in {} and {})".format(
                            name, self.items[name], conf_cls
                        )
                    )
                self.items[name] = conf_cls

    def _getinstance(self, name):
        if name not in self.items:
            raise NameError("No such configuration: {}".format(name))
        return self.items[name]()

    def __getitem__(self, name):
        return self.get(name)

    def get(self, name):
        return self._getinstance(name).get(name, dir)

    def getroot(self, name, indicate_default=False):
        return self._getinstance(name).getroot(name, self, indicate_default)

    def setroot(self, name, value, safe=False):
        self._getinstance(name).setroot(name, value, self, safe)

    def deleteroot(self, name):
        self._getinstance(name).deleteroot(name, self)

    def list(self):
        click.echo()
        mx = max([len(n) for n in self.items]) + 1
        for n, cls in self.items.items():
            try:
                d, v = self.getroot(n, indicate_default=True)
                if issubclass(cls, Secret):
                    v = "[…]"
            except ValueError as e:
                sign, v = click.style("✖ {}".format(e), fg="yellow"), ""
            except ConfigMissing:
                sign, v = click.style("− ", fg="red", bold=True), ""
            else:
                if d:
                    sign = click.style("○ ", fg="green")
                else:
                    sign = click.style("● ", fg="green")
            click.secho("{0:>{1}} ".format(n, mx), bold=True, nl=False)
            click.echo(cls.indicator[0] + " ", nl=False)
            click.echo(sign, nl=False)
            click.echo(v)
        click.echo()

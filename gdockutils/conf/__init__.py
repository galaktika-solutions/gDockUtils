import importlib
import os
import inspect

import click

from ..exceptions import ConfigMissing, ImproperlyConfigured
from .sections import SecretSection
from .configfields import ConfigField
from ..utils import path_check, root_mode_needed


def fb(var, envvar, default):
    return var or os.environ.get(envvar, default)


class Config:
    def __init__(
        self,
        config_module=None,
        env_file=None,
        secret_file=None,
        secret_dir=None,
        root_mode=False,
    ):
        stat = os.stat(".")
        self.pu, self.pg = stat.st_uid, stat.st_gid
        self.is_dev = os.path.isdir(".git")
        self.root_mode = root_mode

        if not self.is_dev and self.pu != 0:
            msg = "In production the project directory must be owned by root."
            raise ImproperlyConfigured(msg)

        self.config_module = fb(config_module, "GSTACK_CONFIG_MODULE", "gstack_conf")
        self.env_file = fb(env_file, "GSTACK_ENV_FILE", "/host/.env")
        self.secret_file = fb(secret_file, "GSTACK_SECRET_FILE", "/host/.secret.env")
        self.secret_dir = fb(secret_dir, "GSTACK_SECRET_DIR", "/run/secrets")

        self._ensure_files()

        mod = importlib.import_module(self.config_module)
        self.configmap = {}  # map a config name to the section where it's defined
        self.sections = {}
        sections = inspect.getmembers(mod, inspect.isclass)
        sections = filter(lambda x: hasattr(x[1], "_section_counter"), sections)
        sections = sorted(sections, key=lambda x: x[1]._section_counter)
        for classname, cls in sections:
            fields = inspect.getmembers(cls)
            fields = filter(lambda x: isinstance(x[1], ConfigField), fields)
            fields = sorted(fields, key=lambda x: x[1]._configfield_counter)
            if not fields:
                continue

            instance = cls()
            s = self.sections[instance.get_name()] = []
            for name, _ in fields:
                if name not in self.configmap:
                    self.configmap[name] = instance
                    s.append(name)
                    continue
                msg = "Config field {} is defined in {} and {}"
                othername = self.configmap[name].__class__.__name__
                raise ImproperlyConfigured(msg.format(name, othername, classname))

    def _ensure_files(self):
        # env file
        dirpath = os.path.dirname(os.path.abspath(self.env_file))
        if not os.path.isdir(dirpath):
            raise ImproperlyConfigured("No such directory: {}".format(dirpath))
        path_check(dirpath, self.pu, self.pg, 0o22, self.root_mode)
        path_check(self.env_file, self.pu, self.pg, 0o133, self.root_mode, True)

        # secret_file
        dirpath = os.path.dirname(os.path.abspath(self.secret_file))
        if not os.path.isdir(dirpath):
            raise ImproperlyConfigured("No such directory: {}".format(dirpath))
        path_check(dirpath, self.pu, self.pg, 0o22, self.root_mode)
        path_check(self.secret_file, self.pu, self.pg, 0o177, self.root_mode, True)

        # secret_dir
        if not os.path.isdir(self.secret_dir):
            if self.root_mode:
                os.makedirs(self.secret_dir)
            else:
                msg = "No such directory: {}".format(self.secret_dir)
                raise ImproperlyConfigured(msg)
        path_check(self.secret_dir, 0, 0, 0o22, self.root_mode)

    def _getsection(self, name):
        if name not in self.configmap:
            raise KeyError("No such config: {}".format(name))
        return self.configmap[name]

    def _get(self, name):
        return self._getsection(name).get(name, self)

    def _getroot(self, name, indicate_default=False):
        try:
            return self._getsection(name).getroot(name, self, indicate_default)
        except ConfigMissing:
            raise ConfigMissing("{}: Not set.".format(name))
        except ValueError as e:
            raise ValueError("{}: {}".format(name, e))

    @root_mode_needed
    def set(self, name, value, safe=False):
        try:
            self._getsection(name).setroot(name, value, self, safe)
        except ValueError as e:
            raise ValueError("{}: {}".format(name, e))

    @root_mode_needed
    def delete(self, name):
        self._getsection(name).deleteroot(name, self)

    @root_mode_needed
    def list(self, color=None, file=None):
        s = ""
        for section, fields in self.sections.items():
            s += click.style("\n{}\n\n".format(section), fg="yellow", bold=True)
            mx = max([len(f) for f in fields] or [0])
            for field in fields:
                try:
                    d, v = self._getroot(field, indicate_default=True)
                except ValueError as e:
                    sign, v = click.style("✖", fg="yellow"), str(e)
                except ConfigMissing:
                    sign, v = click.style("−", fg="red", bold=True), ""
                else:
                    if d:
                        sign = click.style("○", fg="green")
                    else:
                        sign = click.style("●", fg="green")
                if isinstance(self.configmap[field], SecretSection):
                    v = "[…]"
                ind = self.configmap[field].indicator[1 if color in (False,) else 0]
                s += click.style(" {0:<{1}} ".format(field, mx), bold=True)
                s += "{} {} {}\n".format(ind, sign, v)
        click.echo(s, color=color, file=file)

    def __getitem__(self, name):
        return self._getroot(name) if self.root_mode else self._get(name)

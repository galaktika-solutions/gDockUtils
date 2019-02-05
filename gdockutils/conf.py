import os
import importlib
import inspect
import re
import base64

import click


ENV_REGEX = re.compile(r"^\s*([^#].*?)=(.*)$")


class NotSet:
    pass


class ConfigType:
    def __init__(self, default=NotSet):
        self.default = default

    def finalize(self, name, value):
        if value is None:
            if self.default != NotSet:
                return self.default
            raise ConfigMissing("The config value {} is missing".format(name))
        return value


class Bool(ConfigType):
    def finalize(self, name, value):
        value = super().finalize(name, value)
        if value in ("True", b"True", True):
            return True
        elif value in ("False", b"False", False):
            return False
        raise ValueError("The value of {} must be `True` or `False`.".format(name))

    def repr(self, name, value):
        if not isinstance(value, bool):
            raise ValueError("The value of {} must be `bool`.".format(name))
        return repr(value)


class ImproperlyConfigured(Exception):
    pass


class ConfigAlreadyExists(Exception):
    pass


class ConfigMissing(Exception):
    pass


class ConfigMeta(type):
    creation_counter = 0

    def __init__(self, name, bases, dict):
        self._gdockutils_order = ConfigMeta.creation_counter
        ConfigMeta.creation_counter += 1


class ConfigItem(metaclass=ConfigMeta):
    names = {}

    def readenv(self, name, file):
        with open(file, "r") as f:
            for l in f.readlines():
                m = ENV_REGEX.match(l)
                if m and m.group(1) == name:
                    return m.group(2)
        return None

    def getroot(self, name, file=None, indicate_default=False):
        file = file or self.file
        ret = self.readenv(name, file)
        default_used = True
        if ret is not None:
            ret = self.decode(ret)
            default_used = False

        ret = self.finalize(name, ret)
        return (default_used, ret) if indicate_default else ret

    def decode(self, value):
        return value

    def encode(self, value):
        return value

    def finalize(self, name, value):
        return self.names[name].finalize(name, value)

    def set(self, name, value, file=None, force=False):
        value = self.names[name].repr(name, value)
        value = self.encode(value)
        file = file or self.file
        newlines = []
        done = False
        with open(file, "r") as f:
            lines = f.readlines()
        for l in lines:
            if done:
                newlines.append(l)
                continue
            m = ENV_REGEX.match(l)
            if m and m.group(1) == name:
                if force:
                    newlines.append("{}={}\n".format(name, value))
                    done = True
                else:
                    msg = "The config {} already set. Use `force` to override."
                    raise ConfigAlreadyExists(msg.format(name))
            else:
                newlines.append(l)
        if not done:
            newlines.append("{}={}\n".format(name, value))
        with open(file, "w") as f:
            f.writelines(newlines)


class Secret(ConfigItem):
    services = {}

    @property
    def file(self):
        return os.environ.get("GSTACK_SECRET_FILE", ".secret.env")

    def decode(self, value):
        return base64.b64decode(value.strip())

    def encode(self, value):
        if isinstance(value, str):
            value = value.encode()
        return base64.b64encode(value).decode()

    def get(self, name, dir=None):
        dir = dir or os.environ.get("GSTACK_SECRET_DIR", "/run/secrets")
        fn = os.path.join(dir, name)
        with open(fn, "rb") as f:
            return self.finalize(name, f.read())


class Env(ConfigItem):
    @property
    def file(self):
        return os.environ.get("GSTACK_ENV_FILE", ".env")

    def get(self, name, dir=None):
        return self.finalize(name, os.environ.get(name))


class Config:
    def __init__(self, config_module=None):
        self.config_module = config_module or os.environ.get(
            "GSTACK_CONFIG_MODULE", "gstack_conf"
        )
        mod = importlib.import_module(self.config_module)
        self.items = {}
        classes = [
            c[1]
            for c in inspect.getmembers(mod)
            if hasattr(c[1], '_gdockutils_order')
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

    def getroot(self, name, file=None, indicate_default=False):
        return self._getinstance(name).getroot(name, file, indicate_default)

    def get(self, name, dir=None):
        return self._getinstance(name).get(name, dir)

    def set(self, name, value, file=None, force=False):
        self._getinstance(name).set(name, value, file, force)

    def list(self, envfile=None, secretfile=None):
        click.echo()
        mx = max([len(n) for n in self.items]) + 1
        for n, cls in self.items.items():
            if issubclass(cls, Secret):
                file = secretfile
            else:
                file = envfile
            try:
                d, v = self.getroot(n, file=file, indicate_default=True)
                if issubclass(cls, Secret):
                    # v = r'¯\_(ツ)_/¯'
                    v = '[…]'
            except ValueError:
                sign, v = click.style('✖ ', fg='yellow'), ''
            except ConfigMissing:
                sign, v = click.style('− ', fg='red', bold=True), ''
            else:
                if d:
                    sign = click.style('● ', fg='green')
                else:
                    sign = click.style('✔ ', fg='green')
            click.secho('{0:>{1}} '.format(n, mx), bold=True, nl=False)
            click.echo(sign, nl=False)
            click.echo(v)
        click.echo()

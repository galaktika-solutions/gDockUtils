import re
import os
import base64
import threading

from ..exceptions import ConfigAlreadyExists, ConfigMissing, ImproperlyConfigured
from .configfields import ConfigField


ENV_REGEX = re.compile(r"^\s*([^#].*?)=(.*)$")
_section_counter = threading.local()
_section_counter.i = 0


class SectionMeta(type):
    """Metaclass to keep track of config ordering."""

    def __init__(self, name, bases, dict):
        if bases and "SectionBase" not in [b.__name__ for b in bases]:
            self._section_counter = _section_counter.i
            _section_counter.i += 1


class SectionBase(metaclass=SectionMeta):
    name = ""
    indicator = ("?", "?")

    def _check_config(self):
        pass

    def get_name(self):
        return self.name if self.name else "Section {}".format(self._section_counter)

    def to_python(self, name, value):
        return getattr(self, name).to_python(value)

    def readenv(self, name, file):
        with open(file, "r") as f:
            for l in f.readlines():
                m = ENV_REGEX.match(l)
                if m and m.group(1) == name:
                    return m.group(2)
        return None

    def getroot(self, name, config, indicate_default=False):
        file = self.get_file(config)
        ret = self.readenv(name, file)
        default_used = True
        if ret is not None:
            ret = self.decode(ret)
            default_used = False

        ret = getattr(self, name).to_python(ret)
        return (default_used, ret) if indicate_default else ret

    def decode(self, value):
        return value

    def encode(self, value):
        return value

    def _set_delete(self, name, value, config, safe=False, set=True):
        file = self.get_file(config)
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
                done = True
                if set:  # if we delete, just leave this line alone
                    if not safe:
                        newlines.append("{}={}\n".format(name, value))
                    else:
                        msg = "The config {} already set and safe mode requested."
                        raise ConfigAlreadyExists(msg.format(name))
            else:
                newlines.append(l)
        if not done and set:
            newlines.append("{}={}\n".format(name, value))
        with open(file, "w") as f:
            f.writelines(newlines)

    def setroot(self, name, value, config, safe=False):
        value = getattr(self, name).to_repr(value)
        value = self.encode(value)
        self._set_delete(name, value, config, safe=safe)

    def deleteroot(self, name, config):
        self._set_delete(name, None, config, safe=None, set=False)


class SecretSection(SectionBase):
    services = {}
    indicator = ("S", "S")

    def _check_config(self):
        services = {}  # keep a cleaned version on the instance
        for service, secrets in self.services.items():
            clean_secrets = []
            for secret in secrets:
                if isinstance(secret, str):
                    secret = [secret]
                if not hasattr(self, secret[0]) or not isinstance(
                    getattr(self, secret[0]), ConfigField
                ):
                    raise ImproperlyConfigured(
                        "Invalid name for service {} in section {}: {}".format(
                            service, self.__class__.__name__, secret[0]
                        )
                    )
                clean_secrets.append((
                    secret[0],
                    secret[1] if len(secret) >= 2 else service,
                    secret[2] if len(secret) >= 2 else service,
                    secret[3] if len(secret) >= 3 else 0o400,
                ))
            if clean_secrets:
                services[service] = clean_secrets
        self.services = services

    def decode(self, value):
        return base64.b64decode(value.strip())

    def get_file(self, config):
        return config.secret_file

    def encode(self, value):
        if isinstance(value, str):
            value = value.encode()
        return base64.b64encode(value).decode()

    def get(self, name, config):
        fn = os.path.join(config.secret_dir, name)
        try:
            with open(fn, "rb") as f:
                content = f.read()
        except FileNotFoundError:
            content = None
        except PermissionError:
            raise ConfigMissing("Accessing the secret {} is forbidden.".format(name))
        return getattr(self, name).to_python(content)


class EnvSection(SectionBase):
    indicator = ("E", "E")

    def get_file(self, config):
        return config.env_file

    def get(self, name, config):
        try:
            return getattr(self, name).to_python(os.environ.get(name))
        except KeyError:
            raise ConfigMissing("The variable {} is not set.".format(name))

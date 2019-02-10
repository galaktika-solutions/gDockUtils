import re
import os
import base64

from .exceptions import ConfigAlreadyExists, ConfigMissing


ENV_REGEX = re.compile(r"^\s*([^#].*?)=(.*)$")


class ConfigMeta(type):
    """Metaclass the keep track of config ordering."""
    creation_counter = 0

    def __init__(self, name, bases, dict):
        self._gdockutils_order = ConfigMeta.creation_counter
        ConfigMeta.creation_counter += 1


class ConfigItem(metaclass=ConfigMeta):
    names = {}
    section = 'Main'

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

        ret = self.names[name].to_python(name, ret)
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
        value = self.names[name].to_repr(name, value)
        value = self.encode(value)
        self._set_delete(name, value, config, safe=safe)

    def deleteroot(self, name, config):
        self._set_delete(name, None, config, safe=None, set=False)


class Secret(ConfigItem):
    services = {}
    indicator = ('🔐', 'S')

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
                return self.names[name].to_python(name, f.read())
        except FileNotFoundError:
            raise ConfigMissing("The secret {} not found.".format(name))
        except PermissionError:
            raise ConfigMissing("Accessing the secret {} is forbidden.".format(name))


class Env(ConfigItem):
    indicator = ('🔓', 'E')

    def get_file(self, config):
        return config.env_file

    def get(self, name, config):
        return self.names[name].to_python(name, os.environ.get(name))

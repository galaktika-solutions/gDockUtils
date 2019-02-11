import threading

from ..exceptions import ConfigMissing


_configfield_counter = threading.local()
_configfield_counter.i = 0


class NotSet:
    """A special type for `default`.

    Indicates that a default value does not exist, which means the config is
    required.
    """

    pass


class ConfigFieldMeta(type):
    """Metaclass to keep track of field ordering."""

    def __init__(self, name, bases, dict):
        self._configfield_counter = _configfield_counter.i
        _configfield_counter.i += 1


class ConfigField(metaclass=ConfigFieldMeta):
    convert_needs_string = True

    def __init__(self, default=NotSet):
        self.default = default

    def to_python(self, value):
        """Converts the stored config value to python.

        Given the settings value as string or bytes, performs validation and
        returns the python value. May raise ConfigMissing or ValueError.
        """
        if value is None:
            if self.default != NotSet:
                return self.default
            raise ConfigMissing()
        if isinstance(value, bytes) and self.convert_needs_string:
            value = value.decode()
        return self.convert_to_python(value)

    def to_repr(self, value):
        """Converts the value to string/bytes for storage.

        May raises ValueError.
        """
        return repr(value)


class Bool(ConfigField):
    def convert_to_python(self, value):
        if value in ("True", True):
            return True
        elif value in ("False", False):
            return False
        raise ValueError("Must be `True` or `False`.")

    def to_repr(self, value):
        if not isinstance(value, bool):
            raise ValueError("Must be True or False.")
        return repr(value)


class String(ConfigField):
    def __init__(self, default=NotSet, min_length=None, max_length=None):
        super().__init__(default=default)
        self.min_length = min_length
        self.max_length = max_length

    def validate_python(self, value):
        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError("Too short ({} < {})".format(len(value), self.min_length))
        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError("Too long ({} > {}).".format(len(value), self.max_length))
        return value

    def convert_to_python(self, value):
        return self.validate_python(value)

    def to_repr(self, value):
        if not isinstance(value, str):
            raise ValueError("Must be string.")
        return self.validate_python(value)


class Int(ConfigField):
    def __init__(self, default=NotSet, min_value=None, max_value=None):
        super().__init__(default=default)
        self.min_value = min_value
        self.max_value = max_value

    def validate_python(self, value):
        if self.min_value is not None and value < self.min_value:
            raise ValueError("Too small ({} < {}).".format(value, self.min_value))
        if self.max_value is not None and value > self.max_value:
            raise ValueError("Too large ({} > {}).".format(value, self.max_value))
        return value

    def convert_to_python(self, value):
        value = int(value)  # raises ValueError
        return self.validate_python(value)

    def to_repr(self, value):
        if not isinstance(value, int):
            raise ValueError("Must be integer.")
        return str(self.validate_python(value))

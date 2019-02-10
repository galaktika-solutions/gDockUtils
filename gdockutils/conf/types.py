from .exceptions import ConfigMissing


class NotSet:
    pass


class ConfigType:
    def __init__(self, default=NotSet):
        self.default = default

    def to_python(self, name, value):
        """Converts the stored config value to python.

        Given the settings value as string or bytes, performs validation and
        returns the python value. May raise ConfigMissing or ValueError.
        """
        if value is None:
            if self.default != NotSet:
                return self.default
            raise ConfigMissing("The config value {} is missing".format(name))
        if isinstance(value, bytes):
            value = value.decode()
        return self.convert_to_python(name, value)

    def to_repr(self, name, value):
        """Converts the value to string/bytes for storage.

        May raises ValueError.
        """
        return repr(value)


class Bool(ConfigType):
    def convert_to_python(self, name, value):
        if value in ("True", True):
            return True
        elif value in ("False", False):
            return False
        raise ValueError("The value of {} must be `True` or `False`.".format(name))

    def to_repr(self, name, value):
        if not isinstance(value, bool):
            raise ValueError("The value of {} must be `bool`.".format(name))
        return repr(value)


class String(ConfigType):
    def __init__(self, default=NotSet, min_length=None, max_length=None):
        super().__init__(default=default)
        self.min_length = min_length
        self.max_length = max_length

    def validate_python(self, name, value):
        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError("The value of {} is too short.".format(name))
        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError("The value of {} is too long.".format(name))
        return value

    def convert_to_python(self, name, value):
        return self.validate_python(name, value)

    def to_repr(self, name, value):
        if not isinstance(value, str):
            raise ValueError("The value of {} must be string.".format(name))
        return self.validate_python(name, value)


class Int(ConfigType):
    def __init__(self, default=NotSet, min_value=None, max_value=None):
        super().__init__(default=default)
        self.min_value = min_value
        self.max_value = max_value

    def validate_python(self, name, value):
        if self.min_value is not None and value < self.min_value:
            raise ValueError("The value of {} is too small.".format(name))
        if self.max_value is not None and value > self.max_value:
            raise ValueError("The value of {} is too large.".format(name))
        return value

    def convert_to_python(self, name, value):
        value = int(value)  # raises ValueError
        return self.validate_python(name, value)

    def to_repr(self, name, value):
        if not isinstance(value, int):
            raise ValueError("The value of {} must be integer.".format(name))
        return str(self.validate_python(name, value))

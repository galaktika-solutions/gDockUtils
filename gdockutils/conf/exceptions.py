class ImproperlyConfigured(Exception):
    """Raised when the internal gstack configuration is invalid."""
    pass


class ConfigAlreadyExists(Exception):
    pass


class ConfigMissing(Exception):
    """Raised when a required config value is missing."""
    pass

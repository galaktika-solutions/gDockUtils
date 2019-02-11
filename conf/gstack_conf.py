from gdockutils.conf.sections import SecretSection
from gdockutils.conf.configfields import String


class Other(SecretSection):
    name = "pypi credentials"

    PYPI_USERNAME = String()
    PYPI_PASSWORD = String()

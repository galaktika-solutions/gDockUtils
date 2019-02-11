from gdockutils.conf.sections import EnvSection, SecretSection
from gdockutils.conf.configfields import Bool, String, Int


class Env(EnvSection):
    A = Bool(default=True)
    B = String(min_length=5)
    C = String()


class Other(SecretSection):
    name = "Other Section"

    X = Int(max_value=100)
    Y = String(default='foo', max_length=10)


class Empty(EnvSection):
    pass

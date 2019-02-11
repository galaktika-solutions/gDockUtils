from gdockutils.conf.sections import EnvSection, SecretSection
from gdockutils.conf.configfields import Bool, String, Int


class Env(EnvSection):
    A = Bool(default=True)
    B = String(min_length=5)


class Other(SecretSection):
    name = "Other Section"

    X = Int(max_value=200)
    Y = String(default="foo")

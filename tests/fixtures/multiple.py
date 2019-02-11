from gdockutils.conf.sections import EnvSection, SecretSection
from gdockutils.conf.configfields import Bool, Int


class Env(EnvSection):
    A = Bool(default=True)


class Other(SecretSection):
    A = Int(max_value=200)

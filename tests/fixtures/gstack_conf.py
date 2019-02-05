from gdockutils import conf


class TestSecret(conf.Secret):
    names = {"SECRET": conf.Bool()}


class TestEnv(conf.Env):
    names = {"TEST": conf.Bool(default=False)}

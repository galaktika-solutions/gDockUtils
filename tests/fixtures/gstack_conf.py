from gdockutils.conf.items import Secret, Env
from gdockutils.conf.types import Bool, String, Int


class TestEnv(Env):
    names = {
        "TEST": Bool(default=False),
        "REPORTNAME": String(default="report", max_length=10),
    }


class TestSecret(Secret):
    """Secrets for Testing

    Use it with caution.
    """

    section = "Database"
    names = {
        "SECRET": Bool(),
        "USERNAME": String(min_length=5),
        "WIFEAGE": Int(min_value=18, max_value=150),
    }
    services: {"postgres": {"USERNAME": 0x400}}

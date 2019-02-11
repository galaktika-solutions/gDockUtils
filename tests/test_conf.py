import unittest
import sys
import glob
import os
from unittest.mock import patch

from gdockutils.conf import Config
from gdockutils.exceptions import ImproperlyConfigured, RootModeNeeded


sys.path += ["/src/tests/fixtures"]


class TestConf(unittest.TestCase):
    def setUp(self):
        """Deletes the conf directory."""
        files = glob.glob("/src/tests/conf/.*")
        for f in files:
            os.remove(f)
        os.chdir("/src")

    def config(
        self,
        module="conf1",
        env_file="/src/tests/conf/.env",
        secret_file="/src/tests/conf/.secret.env",
        secret_dir=None,
        root_mode=True,
    ):
        return Config(
            config_module=module,
            env_file=env_file,
            secret_file=secret_file,
            secret_dir=secret_dir,
            root_mode=root_mode,
        )

    def test_wont_create_without_root_mode(self):
        with self.assertRaises(ImproperlyConfigured):
            self.config(root_mode=False)

    def test_wont_set_without_root_mode(self):
        self.config()
        with self.assertRaises(RootModeNeeded):
            self.config(root_mode=False).set("A", True)

    def test_will_set_in_root_mode(self):
        self.config().set("B", "asdfgh")
        self.assertEqual(self.config()["B"], "asdfgh")

    def test_list(self):
        config = self.config(module="list_test")
        config.set("X", 150)
        config.set("B", "gdockutils is cool :)")
        config = self.config(module="conf1")
        with patch("sys.stdout.write") as mock:
            config.list(color=False)
            args = mock.call_args[0][0].decode()

        args = args.splitlines()
        self.assertEqual(len(args), 12)

    def test_errors_handled(self):
        os.chdir("/src/tests")
        with self.assertRaises(ImproperlyConfigured):
            self.config()
        os.chdir("/src")
        with self.assertRaises(ImproperlyConfigured):
            self.config(module="multiple")
        with self.assertRaises(ImproperlyConfigured):
            self.config(env_file="/x/.env")
        with self.assertRaises(ImproperlyConfigured):
            self.config(secret_file="/x/.secret.env")
        with self.assertRaises(ImproperlyConfigured):
            self.config(secret_dir="/run/x", root_mode=False)
        conf = self.config()
        with self.assertRaises(KeyError):
            conf["FOO"]
        with self.assertRaises(ValueError):
            conf.set("Y", "12345678901")  # too long
        conf.delete("Y")

    def test_simple_get(self):
        self.config()
        self.assertEqual(self.config(root_mode=False)["A"], True)

    def test_bool(self):
        conf = self.config()
        conf.set("A", True)
        self.assertEqual(conf["A"], True)
        conf.set("A", False)
        self.assertEqual(conf["A"], False)
        with open(conf.env_file, 'w') as f:
            f.write("A=xxx")
        with self.assertRaises(ValueError):
            conf["A"]
        with self.assertRaises(ValueError):
            conf.set("A", "x")

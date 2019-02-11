import unittest
import unittest.mock

from gdockutils import parseuidgid


class TestUtils(unittest.TestCase):
    def test_parseuidgid(self):
        self.assertEqual(parseuidgid("1:3"), (1, 3))
        self.assertEqual(parseuidgid("postgres"), (999, 999))
        self.assertEqual(parseuidgid("postgres:0"), (999, 0))
        self.assertEqual(parseuidgid("postgres:django"), (999, 8000))

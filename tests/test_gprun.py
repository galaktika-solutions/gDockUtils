import unittest
import unittest.mock
import sys
import os

from gdockutils.cli import gprun


class TestCertificates(unittest.TestCase):
    def test_it_works(self):
        with unittest.mock.patch.object(
            sys, 'argv', ['gprun', '-u', '1234:2345', 'touch', '/tmp/x']
        ):
            with self.assertRaises(SystemExit):
                gprun()
        stat = os.stat('/tmp/x')
        self.assertEqual(stat.st_uid, 1234)
        self.assertEqual(stat.st_gid, 2345)

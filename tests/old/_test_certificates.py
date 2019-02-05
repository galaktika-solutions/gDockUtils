import sys
import unittest
import unittest.mock
import io
import os

from gdockutils.cli import createcerts


class TestCertificates(unittest.TestCase):
    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_fails_without_args(self, mock_stderr):
        with unittest.mock.patch.object(sys, 'argv', ['createcerts']):
            with self.assertRaises(SystemExit):
                createcerts()
            self.assertTrue(
                'At least one host name must be specified.'
                in mock_stderr.getvalue()
            )

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_fails_without_name(self, mock_stderr):
        with unittest.mock.patch.object(
            sys, 'argv', ['createcerts', '-i', '']
        ):
            with self.assertRaises(SystemExit):
                createcerts()
            self.assertTrue(
                'At least one host name must be specified.'
                in mock_stderr.getvalue()
            )

    def test_create(self):
        with unittest.mock.patch.object(
            sys, 'argv', ['createcerts', '-n', 'test', '-n', 'test2']
        ):
            createcerts()
        self.assertEqual(len(os.listdir('.files')), 3)
        for f in os.listdir('.files'):
            os.remove(os.path.join('.files', f))

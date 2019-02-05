import unittest
from unittest import mock
import os
import subprocess
import shutil

from gdockutils.db import ensure_db, wait_for_db
from gdockutils.prepare import prepare
from gdockutils import PGDATA
from .utils import RecordingPopen


class TestEnsureDB(unittest.TestCase):
    """For these tests the database must not be running.

    After each test the traces of the database are removed.
    """

    @classmethod
    def setUpClass(cls):
        os.chdir('project')

    @classmethod
    def tearDownClass(cls):
        os.chdir('..')

    def tearDown(self):
        shutil.rmtree(PGDATA)
        RecordingPopen.clear()

    def test_ensure_db(self):
        with mock.patch('gdockutils.gprun.subprocess.Popen', RecordingPopen):
            ensure_db()
            db = subprocess.Popen(
                ['gprun', '-u', 'postgres', 'postgres'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        with mock.patch.dict('gdockutils.db.DB_ENV', {'PGHOST': 'localhost'}):
            prepare('dbclient', user='0')
            wait_for_db(noprint=True)
        db.terminate()
        db.wait()


class TestDBRelated(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir('project')
        subprocess.run(
            ['ensure_db'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        cls.db_process = subprocess.Popen(
            ['gprun', '-u', 'postgres', 'postgres'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    @classmethod
    def tearDownClass(cls):
        cls.db_process.terminate()
        cls.db_process.wait()
        shutil.rmtree(PGDATA)
        os.chdir('..')

    def tearDown(self):
        for f in os.listdir('/run/secrets'):
            os.remove(os.path.join('/run/secrets', f))

    def test_testing_itself(self):
        self.assertTrue(True)

    def test_we_are_root(self):
        self.assertEqual((os.getuid(), os.getgid()), (0, 0))

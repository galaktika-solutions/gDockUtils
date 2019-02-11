import unittest
from unittest.mock import patch

from gdockutils.utils import run


class TestUtils(unittest.TestCase):
    @patch("gdockutils.utils.subprocess.run")
    def test_run(self, mock_run):
        run(["ls"])
        mock_run.assert_called()

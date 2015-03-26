import os
from unittest import TestCase
import sys

from mock import patch

import libfaketime


class TestReexec(TestCase):
    def _assert_successful_reexec(self, exec_patch):
        expected_environ = os.environ.copy()
        expected_environ.update(libfaketime.get_env_additions()[1])

        libfaketime.reexec_if_needed()

        exec_patch.assert_called_once_with(
            sys.executable, [sys.executable] + sys.argv, expected_environ
        )

    @patch('os.execve')
    @patch('sys.platform', 'linux2')
    def test_reexec_linux_succeeds(self, exec_patch):
        self._assert_successful_reexec(exec_patch)

    @patch('os.execve')
    @patch('sys.platform', 'darwin')
    def test_reexec_osx_succeeds(self, exec_patch):
        self._assert_successful_reexec(exec_patch)

    @patch('os.execve')
    @patch('sys.platform', 'win32')
    def test_reexec_windows_fails(self, exec_patch):
        self.assertRaises(RuntimeError, libfaketime.reexec_if_needed)

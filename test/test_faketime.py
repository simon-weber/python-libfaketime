import datetime
import os
from unittest import TestCase
import sys

from mock import patch

import libfaketime
from libfaketime import fake_time


class TestReexec(TestCase):
    def _assert_successful_reexec(self, exec_patch):
        expected_environ = os.environ.copy()
        expected_environ.update(libfaketime.get_reload_information()[1])

        libfaketime.reexec_if_needed()

        exec_patch.assert_called_once_with(
            sys.executable, [sys.executable] + sys.argv, expected_environ
        )

    @patch('os.execve')
    @patch('sys.platform', 'linux2')
    def test_reexec_linux_succeeds(self, exec_patch):
        needs_reload, env_additions = libfaketime.get_reload_information()

        # We're actually running with libfaketime loaded in right now, but
        # because we used remove_vars=True, this will return True.
        self.assertTrue(needs_reload)
        self.assertEqual(len(env_additions), 1)

        self._assert_successful_reexec(exec_patch)

    @patch('os.execve')
    @patch('sys.platform', 'darwin')
    def test_reexec_osx_succeeds(self, exec_patch):
        needs_reload, env_additions = libfaketime.get_reload_information()
        self.assertTrue(needs_reload)
        self.assertEqual(len(env_additions), 2)

        self._assert_successful_reexec(exec_patch)

    @patch('os.execve')
    @patch('sys.platform', 'win32')
    def test_reexec_windows_fails(self, exec_patch):
        self.assertRaises(RuntimeError, libfaketime.reexec_if_needed)


class TestFaketime(TestCase):
    def test_nonfake_time_is_dynamic(self):
        # This just makes sure that non-faked time is dynamic;
        # I can't think of a good way to check that the non-faked time is "real".

        first = datetime.datetime.now().microsecond
        second = datetime.datetime.now().microsecond

        self.assertGreater(second, first)

    @fake_time(datetime.datetime.now())
    def test_fake_time_is_static(self):
        first = datetime.datetime.now().microsecond
        second = datetime.datetime.now().microsecond

        self.assertEqual(second, first)

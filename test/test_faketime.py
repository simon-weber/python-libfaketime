import datetime
from unittest import TestCase

from mock import patch

import libfaketime
from libfaketime import fake_time


class TestReexec(TestCase):
    @patch('os.execve')
    @patch('sys.platform', 'win32')
    def test_reexec_windows_fails(self, exec_patch):
        self.assertRaises(RuntimeError, libfaketime.reexec_if_needed)


class TestFaketime(TestCase):
    def _assert_time_not_faked(self):
        # This just makes sure that non-faked time is dynamic;
        # I can't think of a good way to check that the non-faked time is "real".

        first = datetime.datetime.now().microsecond
        second = datetime.datetime.now().microsecond

        self.assertGreater(second, first)

    def test_fake_time_tick(self):
        with fake_time('2000-01-01 10:00:05') as fake:
            self.assertEqual(datetime.datetime.now(), datetime.datetime(2000, 1, 1, 10, 0, 5))
            fake.tick(delta=datetime.timedelta(hours=1))
            self.assertEqual(datetime.datetime.now(), datetime.datetime(2000, 1, 1, 11, 0, 5))

    def test_nonfake_time_is_dynamic(self):
        self._assert_time_not_faked()

    @fake_time(datetime.datetime.now())
    def test_fake_time_is_static(self):
        first = datetime.datetime.now().microsecond
        second = datetime.datetime.now().microsecond

        self.assertEqual(second, first)

    @fake_time('2000-01-01 10:00:05')
    def test_fake_time_parses_easy_strings(self):
        self.assertEqual(datetime.datetime.now(), datetime.datetime(2000, 1, 1, 10, 0, 5))

    @fake_time('march 1st, 2014 at 1:59pm')
    def test_fake_time_parses_tough_strings(self):
        self.assertEqual(datetime.datetime.now(), datetime.datetime(2014, 3, 1, 13, 59))

    @fake_time(datetime.datetime(2014, 1, 1, microsecond=123456))
    def test_fake_time_has_microsecond_granularity(self):
        self.assertEqual(datetime.datetime.now(), datetime.datetime(2014, 1, 1, microsecond=123456))

    def test_nested_fake_time(self):
        self._assert_time_not_faked()

        with fake_time('1/1/2000'):
            self.assertEqual(datetime.datetime.now(), datetime.datetime(2000, 1, 1))

            with fake_time('1/1/2001'):
                self.assertEqual(datetime.datetime.now(), datetime.datetime(2001, 1, 1))

            self.assertEqual(datetime.datetime.now(), datetime.datetime(2000, 1, 1))

        self._assert_time_not_faked()

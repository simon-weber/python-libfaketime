import datetime
import time
import os
import uuid

from mock import patch
import pytest

import libfaketime
from libfaketime import fake_time, freeze_time


class TestReexec():
    @patch('os.execve')
    @patch('sys.platform', 'win32')
    def test_reexec_windows_fails(self, exec_patch):
        with pytest.raises(RuntimeError):
            libfaketime.reexec_if_needed()


class TestFaketime():
    def _assert_time_not_faked(self):
        # This just makes sure that non-faked time is dynamic;
        # I can't think of a good way to check that the non-faked time is "real".

        first = datetime.datetime.now().microsecond
        time.sleep(0.000001)
        second = datetime.datetime.now().microsecond

        assert second > first

    def test_fake_time_tick(self):
        with fake_time('2000-01-01 10:00:05') as fake:
            assert datetime.datetime(2000, 1, 1, 10, 0, 5) == datetime.datetime.now()
            fake.tick(delta=datetime.timedelta(hours=1))
            assert datetime.datetime(2000, 1, 1, 11, 0, 5) == datetime.datetime.now()

    def test_nonfake_time_is_dynamic(self):
        self._assert_time_not_faked()

    @fake_time(datetime.datetime.now())
    def test_fake_time_is_static(self):
        first = datetime.datetime.now().microsecond
        second = datetime.datetime.now().microsecond

        assert second == first

    @fake_time('2000-01-01 10:00:05')
    def test_fake_time_parses_easy_strings(self):
        assert datetime.datetime(2000, 1, 1, 10, 0, 5) == datetime.datetime.now()
        assert datetime.datetime(2000, 1, 1, 10, 0, 5) == datetime.datetime.utcnow()

    def test_fake_time_parses_easy_strings_with_timezones(self):
        with fake_time('2000-01-01 10:00:05', tz_offset=3):
            assert datetime.datetime(2000, 1, 1, 13, 0, 5) == datetime.datetime.now()
            assert datetime.datetime(2000, 1, 1, 10, 0, 5) == datetime.datetime.utcnow()

        with fake_time('2000-01-01 10:00:05', tz_offset=-3):
            assert datetime.datetime(2000, 1, 1, 7, 0, 5) == datetime.datetime.now()
            assert datetime.datetime(2000, 1, 1, 10, 0, 5) == datetime.datetime.utcnow()

    @fake_time('march 1st, 2014 at 1:59pm')
    def test_fake_time_parses_tough_strings(self):
        assert datetime.datetime(2014, 3, 1, 13, 59) == datetime.datetime.now()

    @fake_time(datetime.datetime(2014, 1, 1, microsecond=123456))
    def test_fake_time_has_microsecond_granularity(self):
        assert datetime.datetime(2014, 1, 1, microsecond=123456) == datetime.datetime.now()

    def test_nested_fake_time(self):
        self._assert_time_not_faked()

        with fake_time('1/1/2000'):
            assert datetime.datetime(2000, 1, 1) == datetime.datetime.now()

            with fake_time('1/1/2001'):
                assert datetime.datetime(2001, 1, 1) == datetime.datetime.now()

            assert datetime.datetime(2000, 1, 1) == datetime.datetime.now()

        self._assert_time_not_faked()

    def test_freeze_time_alias(self):
        with freeze_time('2000-01-01 10:00:05'):
            assert datetime.datetime(2000, 1, 1, 10, 0, 5) == datetime.datetime.now()

    def test_monotonic_not_mocked(self):
        assert os.environ['DONT_FAKE_MONOTONIC'] == '1'


class TestUUID1Deadlock():

    @fake_time(datetime.datetime.now())
    def test_uuid1_does_not_deadlock(self):
        """This test will deadlock if we fail to patch a system level uuid library."""
        for i in range(100):
            uuid.uuid1()


@fake_time('2000-01-01')
class TestClassDecorator:

    def test_simple(self):
        assert datetime.datetime(2000, 1, 1) == datetime.datetime.now()
        self._faked_time.tick()
        assert datetime.datetime(2000, 1, 1, 0, 0, 1) == datetime.datetime.now()

    @fake_time('2001-01-01')
    def test_overwrite_with_func_decorator(self):
        assert datetime.datetime(2001, 1, 1) == datetime.datetime.now()

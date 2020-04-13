import datetime
import dateutil.tz
import os

import pytest
from pytz import timezone

from libfaketime import fake_time


def test_timezone_is_restored_after_context_manager_usage():
    """https://github.com/simon-weber/python-libfaketime/issues/43"""
    now1 = datetime.datetime.now()
    utcnow1 = datetime.datetime.utcnow()

    with fake_time(now1):
        datetime.datetime.now()

    now2 = datetime.datetime.now()
    utcnow2 = datetime.datetime.utcnow()

    assert abs((now2 - now1).total_seconds()) < 10
    assert abs((utcnow2 - utcnow1).total_seconds()) < 10


def test_tzinfo_is_normalized():
    """Ensure utcnow() behaves correctly when faking non-UTC timestamps."""
    timezone_to_test_with = timezone('Europe/Brussels')
    time_to_freeze = timezone_to_test_with.localize(datetime.datetime(2017, 1, 2, 15, 2))

    with fake_time(time_to_freeze):
        # The timeshift of Europe/Brussels is UTC+1 in January
        assert datetime.datetime.now() == datetime.datetime(2017, 1, 2, 15, 2)
        assert datetime.datetime.utcnow() == datetime.datetime(2017, 1, 2, 14, 2)


def test_block_setting_of_conflicting_tz_info():
    """Cannot pass in tz_offset when the timestamp already carries a timezone."""
    with pytest.raises(Exception) as exc_info:
        timezone_to_test_with = timezone('America/Havana')
        time_to_freeze = timezone_to_test_with.localize(datetime.datetime(2012, 10, 2, 21, 38))

        with fake_time(time_to_freeze, tz_offset=5):
            pass

    assert str(exc_info.value) == 'Cannot set tz_offset when datetime already has timezone'


@pytest.mark.parametrize("offset", range(-2, 3))
def test_generated_tz_is_valid(offset):
    """https://github.com/simon-weber/python-libfaketime/issues/46"""
    now = datetime.datetime.now()

    with fake_time(now, tz_offset=offset):
        fake_tz = os.environ['TZ']
        timezone(fake_tz)  # should not raise pytzdata.exceptions.TimezoneNotFound


def test_dateutil_tz_is_valid():
    test_dt = datetime.datetime(2017, 1, 2, 15, 2)
    dateutil_tzinfo = dateutil.tz.gettz('UTC')
    dt_dateutil_tzinfo = test_dt.replace(tzinfo=dateutil_tzinfo)

    # Should be compatible with a dateutil tzinfo object, not just pytz
    with fake_time(dt_dateutil_tzinfo):
        assert datetime.datetime.now(tz=dateutil_tzinfo) == dt_dateutil_tzinfo

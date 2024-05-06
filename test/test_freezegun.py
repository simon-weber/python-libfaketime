import datetime
import time

import pytest
from freezegun import freeze_time

from libfaketime import fake_time

# TODO
# - Fix time.localtime
# - Fix time.strftime

# mark these as being used (via eval)
assert time
assert datetime

test_functions = [
    ("datetime.datetime.now", (), {}),
    ("datetime.datetime.utcnow", (), {}),
    ("time.time", (), {}),
    #    ("time.localtime", (), {}),
    #    ("time.strftime", ("%Y-%m-%d %H:%M:%S %Z",), {}),
    ("datetime.date", (), {"year": 1970, "month": 1, "day": 1}),
    ("datetime.datetime", (), {"year": 1970, "month": 1, "day": 1}),
]


@pytest.mark.parametrize("test_function", test_functions)
@pytest.mark.parametrize("tz_offset", [0, 12])
@pytest.mark.parametrize("date_to_freeze", ["1970-01-01 00:00:01"])
def test_compare_against_freezegun_results(test_function, tz_offset, date_to_freeze):
    func_name, args, kwargs = test_function

    with fake_time(date_to_freeze, tz_offset=tz_offset):
        libfaketime_result = eval(func_name)(*args, **kwargs)

    with freeze_time(date_to_freeze, tz_offset=tz_offset):
        freezegun_result = eval(func_name)(*args, **kwargs)

    assert freezegun_result == libfaketime_result

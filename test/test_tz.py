import datetime
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

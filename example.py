import datetime

from libfaketime import fake_time, reexec_if_needed

reexec_if_needed()


@fake_time('2000-01-01 10:00:05')
def test_2000():
    return datetime.datetime.now()


@fake_time(datetime.datetime(2001, 1, 1))
def test_2001():
    return datetime.datetime.now()


@fake_time(datetime.datetime(2004, 1, 1) + datetime.timedelta(microseconds=123456))
def test_nanoseconds():
    return datetime.datetime.now()


def test_real():
    return datetime.datetime.now()

if __name__ == '__main__':
    print test_2000()
    print test_2001()
    with fake_time('2002-01-01 00:00:00'):
        print datetime.datetime.now()

    f = fake_time('2003-01-01 00:00:00')
    f.start()
    print datetime.datetime.now()
    f.stop()

    print test_nanoseconds()

    print test_real()

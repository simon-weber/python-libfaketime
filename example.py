import datetime

from libfaketime import fake_time


@fake_time('2000-01-01 10:00:05')
def test_2000():
    return datetime.datetime.now()


@fake_time(datetime.datetime(2001, 1, 1))
def test_2001():
    return datetime.datetime.now()


def test_real():
    return datetime.datetime.now()

if __name__ == '__main__':
    print test_2000()
    print test_2001()
    with fake_time('2002-01-01 00:00:00'):
        print datetime.datetime.now()
    print test_real()

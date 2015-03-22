import datetime

from libfaketime import fake_time


@fake_time('2000-01-01 10:00:05')
def test1():
    return datetime.datetime.now()


@fake_time(datetime.datetime(2001, 1, 1))
def test2():
    return datetime.datetime.now()


def test3():
    return datetime.datetime.now()

if __name__ == '__main__':
    print test1()
    print test2()
    print test3()

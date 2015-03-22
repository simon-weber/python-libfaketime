import datetime

from libfaketime import fake_time

@fake_time('2003-01-01 10:00:05')
def test1():
    return datetime.datetime.now()


def test2():
    return datetime.datetime.now()

if __name__ == '__main__':
    print test2()
    print test1()

import datetime
import sys
import time

from libfaketime import fake_time as lft_fake_time
from libfaketime import reexec_if_needed
from freezegun import freeze_time as freezegun_fake_time


def sample(faker):
    start = time.perf_counter()

    with faker(datetime.datetime.now()):
        datetime.datetime.now()

    datetime.datetime.now()

    return time.perf_counter() - start

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'freezegun':
        faker = freezegun_fake_time
    else:
        faker = lft_fake_time
        reexec_if_needed()

    iterations = 1000

    print("timing %s executions of %s" % (iterations, faker))

    sum = 0
    for _ in range(iterations):
        sum += sample(faker)

    print(sum, 'seconds')

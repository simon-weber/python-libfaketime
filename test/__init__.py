import os
import subprocess
import sys
from unittest import TestCase

import datetime

import libfaketime


def setup_package():
    ext_dir = os.path.dirname(list(libfaketime._lib_addition[sys.platform[:5]].values())[0])
    ext_dir = os.path.join(ext_dir, '..')
    subprocess.check_call(['make', '-C', ext_dir])

    libfaketime.reexec_if_needed()

    print('(re-execed and compiled prior to test run)')


class BaseFaketimeTest(TestCase):
    def _assert_time_not_faked(self):
        # This just makes sure that non-faked time is dynamic;
        # I can't think of a good way to check that the non-faked time is "real".

        first = datetime.datetime.now().microsecond
        second = datetime.datetime.now().microsecond

        self.assertGreater(second, first)

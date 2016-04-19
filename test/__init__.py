import os
import subprocess
import sys

import libfaketime


def setup_package():
    ext_dir = os.path.dirname(list(libfaketime._lib_addition[sys.platform[:5]].values())[0])
    ext_dir = os.path.join(ext_dir, '..')
    subprocess.check_call(['make', '-C', ext_dir])

    libfaketime.reexec_if_needed()

    print('(re-execed and compiled prior to test run)')

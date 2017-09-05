import os
import libfaketime

def pytest_configure():
    libfaketime.reexec_if_needed()
    _, env_additions = libfaketime.get_reload_information()
    os.environ.update(env_additions)

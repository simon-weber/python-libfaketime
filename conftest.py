import libfaketime

def pytest_configure():
    libfaketime.reexec_if_needed()

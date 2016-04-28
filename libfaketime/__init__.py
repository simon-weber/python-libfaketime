from __future__ import print_function

from copy import deepcopy
import datetime
import os
import sys
import threading
import unittest

from contextdecorator import ContextDecorator
import dateutil.parser

try:
    basestring
except NameError:
    basestring = (str, bytes)

# When using reexec_if_needed, remove_vars=True and a test loader that purges sys.modules
# (like nose), it can be tough to run reexec_if_needed only once.
# This env var is set by reexec to ensure we don't reload more than once.

_DID_REEXEC_VAR = 'FAKETIME_DID_REEXEC'


def _get_shared_lib(basename):
    return os.path.join(
        os.path.dirname(__file__),
        os.path.join('vendor', 'libfaketime', 'src'),
        basename)

# keys are the first 5 chars since we don't care about the version.
_lib_addition = {
    'linux': {
        'LD_PRELOAD': _get_shared_lib('libfaketime.so.1')
    },
    'darwi': {
        'DYLD_INSERT_LIBRARIES': _get_shared_lib('libfaketime.1.dylib'),
    },
}

_other_additions = {
    'darwi': {
        'DYLD_FORCE_FLAT_NAMESPACE': '1',
    },
}

_env_additions = deepcopy(_lib_addition)
for platform, d in list(_other_additions.items()):
    # Just doing a .update wouldn't merge the sub dictionaries.
    _env_additions[platform].update(d)


def get_reload_information():
    try:
        env_additions = _env_additions[sys.platform[:5]]
    except KeyError:
        raise RuntimeError("libfaketime does not support platform %s" % sys.platform)

    needs_reload = os.environ.get(_DID_REEXEC_VAR) != 'true'

    return needs_reload, env_additions


def main():  # pragma: nocover
    """Print the necessary environment to stdout."""

    _, _env_additions = get_reload_information()
    for key, value in _env_additions.items():
        print('export %s="%s"' % (key, value))
    print('export %s=true' % _DID_REEXEC_VAR)


def reexec_if_needed(remove_vars=True):
    needs_reload, env_additions = get_reload_information()
    if needs_reload:
        new_environ = os.environ.copy()
        new_environ.update(env_additions)
        new_environ[_DID_REEXEC_VAR] = 'true'
        args = [sys.executable, [sys.executable] + sys.argv, new_environ]
        print('re-exec with libfaketime dependencies')
        os.execve(*args)

    if remove_vars:
        for key in env_additions:
            if key in os.environ:
                del os.environ[key]


def begin_callback(instance):
    """Called just before faking the time."""
    pass


def end_callback(instance):
    """Called just after finished faking the time."""
    pass


class fake_time(ContextDecorator):
    def __init__(self, datetime_spec, only_main_thread=True):
        self.only_main_thread = only_main_thread

        _datetime = datetime_spec
        if isinstance(datetime_spec, basestring):
            _datetime = dateutil.parser.parse(datetime_spec)

        self.time_to_freeze = _datetime  # freezegun compatibility

    def _should_fake(self):
        return self.only_main_thread and threading.current_thread().name == 'MainThread'

    def _format_datetime(self, _datetime):
        return _datetime.strftime('%Y-%m-%d %T %f')

    def tick(self, delta=datetime.timedelta(seconds=1)):
        self.time_to_freeze += delta
        os.environ['FAKETIME'] = self._format_datetime(self.time_to_freeze)

    def __enter__(self):
        if self._should_fake():
            begin_callback(self)
            self._prev_spec = os.environ.get('FAKETIME')
            os.environ['FAKETIME'] = self._format_datetime(self.time_to_freeze)
        return self

    def __exit__(self, *exc):
        if self._should_fake():
            if self._prev_spec is not None:
                os.environ['FAKETIME'] = self._prev_spec
            else:
                del os.environ['FAKETIME']
                end_callback(self)

        return False

    def __call__(self, decorable):
        if isinstance(decorable, unittest.TestCase):
            # If it's a TestCase, we assume you want to freeze the time for the
            # tests, from setUpClass to tearDownClass
            klass = decorable

            # Use getattr as in Python 2.6 they are optional
            orig_setUpClass = getattr(klass, 'setUpClass', None)
            orig_tearDownClass = getattr(klass, 'tearDownClass', None)

            @classmethod
            def setUpClass(cls):
                self.start()
                if orig_setUpClass is not None:
                    orig_setUpClass()

            @classmethod
            def tearDownClass(cls):
                if orig_tearDownClass is not None:
                    orig_tearDownClass()
                self.stop()

            klass.setUpClass = setUpClass
            klass.tearDownClass = tearDownClass

            return klass

        return super(fake_time, self).__call__(decorable)

    # Freezegun compatibility.
    start = __enter__
    stop = __exit__

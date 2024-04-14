from __future__ import print_function

from copy import deepcopy
import datetime
import dateutil.parser
import functools
import inspect
import os
import sys
import threading
import time
import unittest
import uuid

from pytz import utc, timezone

try:
    basestring
except NameError:
    basestring = (str, bytes)



# When using reexec_if_needed, remove_vars=True and a test loader that purges sys.modules
# (like nose), it can be tough to run reexec_if_needed only once.
# This env var is set by reexec to ensure we don't reload more than once.

_DID_REEXEC_VAR = 'FAKETIME_DID_REEXEC'


def _get_lib_path():
    vendor_dir = 'libfaketime'

    return os.path.join(
        os.path.dirname(__file__),
        os.path.join('vendor', vendor_dir, 'src'))


def _get_shared_lib(basename):
    return os.path.join(_get_lib_path(), basename)


def _setup_ld_preload(soname):
    if 'LD_PRELOAD' in os.environ:
        preload = '{}:{}'.format(soname, os.environ['LD_PRELOAD'])
    else:
        preload = soname

    return preload


# keys are the first 5 chars since we don't care about the version.
_lib_addition = {
    'linux': {
        'LD_LIBRARY_PATH': _get_lib_path(),
        'LD_PRELOAD': _setup_ld_preload('libfaketime.so.1')
    },
    'darwi': {
        'DYLD_INSERT_LIBRARIES': _get_shared_lib('libfaketime.1.dylib'),
    },
}

_other_additions = {
    'linux': {
        'DONT_FAKE_MONOTONIC': '1',
        'FAKETIME_NO_CACHE': '1',
    },
    'darwi': {
        'DONT_FAKE_MONOTONIC': '1',
        'DYLD_FORCE_FLAT_NAMESPACE': '1',
        'FAKETIME_NO_CACHE': '1',
    },
}

_env_additions = deepcopy(_lib_addition)
for platform_name, d in list(_other_additions.items()):
    # Just doing a .update wouldn't merge the sub dictionaries.
    _env_additions[platform_name].update(d)


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


def reexec_if_needed(remove_vars=True, quiet=False):
    needs_reload, env_additions = get_reload_information()
    if needs_reload:
        new_environ = os.environ.copy()
        new_environ.update(env_additions)
        new_environ[_DID_REEXEC_VAR] = 'true'
        args = [sys.executable, [sys.executable] + sys.argv, new_environ]
        if not quiet:
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


class fake_time:
    def __init__(self, datetime_spec, only_main_thread=True, tz_offset=None):
        self.only_main_thread = only_main_thread
        self.timezone_str = 'UTC'
        if tz_offset is not None:
            self.timezone_str = 'Etc/GMT{0:+}'.format(-tz_offset)

        self.time_to_freeze = datetime_spec
        if isinstance(datetime_spec, basestring):
            self.time_to_freeze = utc.localize(dateutil.parser.parse(datetime_spec)) \
                .astimezone(timezone(self.timezone_str))
        elif isinstance(datetime_spec, datetime.datetime):
            if datetime_spec.tzinfo:
                if tz_offset is not None:
                    raise Exception('Cannot set tz_offset when datetime already has timezone')
                self.timezone_str = datetime_spec.tzinfo.tzname(datetime_spec)

    def _should_fake(self):
        return not self.only_main_thread or threading.current_thread().name == 'MainThread'

    _uuid_func_names = (
        # < 3.7
        '_uuid_generate_time',
        # 3.7+
        '_generate_time_safe', '_generate_time')

    def _should_patch_uuid(self):
        # Return the name of the uuid time generate function, or None if not present.
        # This must be patched to avoid uuid1 deadlocks in OS uuid libraries.
        if self._should_fake() and not self._prev_spec:
            for func_name in self._uuid_func_names:
                if hasattr(uuid, func_name):
                    return func_name

        return None

    def _format_datetime(self, _datetime):
        return _datetime.strftime('%Y-%m-%d %T %f')

    def tick(self, delta=datetime.timedelta(seconds=1)):
        self.time_to_freeze += delta
        os.environ['FAKETIME'] = self._format_datetime(self.time_to_freeze)

    def __enter__(self):
        if self._should_fake():
            begin_callback(self)
            self._prev_spec = os.environ.get('FAKETIME')
            self._prev_tz = os.environ.get('TZ')

            os.environ['TZ'] = self.timezone_str

            time.tzset()
            os.environ['FAKETIME'] = self._format_datetime(self.time_to_freeze)

        func_name = self._should_patch_uuid()
        if func_name:
            self._backup_uuid_generate_time = getattr(uuid, func_name)
            setattr(uuid, func_name, None)

        return self

    def __exit__(self, *exc):
        func_name = self._should_patch_uuid()
        if func_name:
            setattr(uuid, func_name, self._backup_uuid_generate_time)

        if self._should_fake():
            if self._prev_tz is not None:
                os.environ['TZ'] = self._prev_tz
            else:
                del os.environ['TZ']
            time.tzset()

            if self._prev_spec is not None:
                os.environ['FAKETIME'] = self._prev_spec
            else:
                del os.environ['FAKETIME']
                end_callback(self)

        return False

    # Freezegun compatibility.
    start = __enter__
    stop = __exit__

    # Decorator-style use support (shamelessly taken from freezegun, see
    # https://github.com/spulec/freezegun/blob/7ad16a5579b28fc939a69cc04f0e99ba5e87b206/freezegun/api.py#L323)

    def __call__(self, func):
        if inspect.isclass(func):
            return self.decorate_class(func)
        return self.decorate_callable(func)

    def decorate_class(self, klass):
        if issubclass(klass, unittest.TestCase):
            # If it's a TestCase, we assume you want to freeze the time for the
            # tests, from setUpClass to tearDownClass

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

        else:

            seen = set()

            klasses = klass.mro() if hasattr(klass, 'mro') else [klass] + list(klass.__bases__)
            for base_klass in klasses:
                for (attr, attr_value) in base_klass.__dict__.items():
                    if attr.startswith('_') or attr in seen:
                        continue
                    seen.add(attr)

                    if not callable(attr_value) or inspect.isclass(attr_value):
                        continue

                    try:
                        setattr(klass, attr, self(attr_value))
                    except (AttributeError, TypeError):
                        # Sometimes we can't set this for built-in types and custom callables
                        continue

        klass._faked_time = self
        return klass

    def decorate_callable(self, func):
        def wrapper(*args, **kwargs):
            with self:
                result = func(*args, **kwargs)
            return result
        functools.update_wrapper(wrapper, func)

        # update_wrapper already sets __wrapped__ in Python 3.2+, this is only
        # needed for Python 2.x support
        wrapper.__wrapped__ = func

        return wrapper


freeze_time = fake_time

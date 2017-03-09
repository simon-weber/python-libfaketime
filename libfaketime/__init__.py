from __future__ import print_function

from copy import deepcopy
import datetime
import os
import sys
import threading
import uuid

import dateutil.parser
import dateutil.tz

try:
    from contextlib import ContextDecorator
except ImportError:
    from contextdecorator import ContextDecorator

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
        return not self.only_main_thread or threading.current_thread().name == 'MainThread'

    def _should_patch_uuid(self):
        return hasattr(uuid, '_uuid_generate_time') and \
               self._should_fake() and \
               not self._prev_spec

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

        if self._should_patch_uuid():
            # Bug fix for uuid1 deadlocks in system level uuid libraries
            # PR: https://github.com/simon-weber/python-libfaketime/pull/14
            self._backup_uuid_generate_time = uuid._uuid_generate_time
            uuid._uuid_generate_time = None

        return self

    def __exit__(self, *exc):
        if self._should_patch_uuid():
            uuid._uuid_generate_time = self._backup_uuid_generate_time

        if self._should_fake():
            if self._prev_spec is not None:
                os.environ['FAKETIME'] = self._prev_spec
            else:
                del os.environ['FAKETIME']
                end_callback(self)

        return False

    # Freezegun compatibility.
    start = __enter__
    stop = __exit__


class freeze_time(fake_time):
    """
    Freeze time honoring timezones. If no time zone is given, freeze_time will interpret the given
    time spec as UTC. It's compatible with freezegun, so it can be used as a drop-in replacement for
    freezegun's freeze_time.
    """

    def __init__(self, spec, tz_offset=None, **kwargs):
        """Fake the time inside decorated function or within context manager

        :param datetime|str spec: the time spec, e.g. "2012-01-14 03:21:34+01000"
        :param int|None tz_offset: Offset the given time by this many hours
        :param dict kwargs: any arguments fake_time might accept
        """
        dt = self._prepare(spec, tz_offset=tz_offset)
        super(freeze_time, self).__init__(dt, **kwargs)

    def _prepare(self, spec, tz_offset=None):
        dt = spec if isinstance(spec, datetime.datetime) else dateutil.parser.parse(spec)

        # If datetime currently has tzinfo, represent it as a datetime in UTC
        utc = self._convert_to_utc(dt)

        # If a tz_offset was given, subtract that also from the datetime
        if tz_offset:
            utc -= datetime.timedelta(hours=tz_offset)

        # Convert the UTC datetime to the local timezone, and remove tzinfo,
        # because the underlying libfaketime, which patches the system time,
        # assumes local timezone and ignores timezone information
        # See https://github.com/simon-weber/python-libfaketime/issues/1 (first issue ;)
        # Maybe one day this will be fixed.

        local = utc.astimezone(dateutil.tz.tzlocal())
        return local.replace(tzinfo=None)

    @staticmethod
    def _convert_to_utc(dt):
        if dt.tzinfo:
            return dt.astimezone(dateutil.tz.tzutc())
        else:
            return dt.replace(tzinfo=dateutil.tz.tzutc())

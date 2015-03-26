from copy import deepcopy
import os
import sys
import threading

from contextdecorator import ContextDecorator
import dateutil.parser


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
for platform, d in _other_additions.items():
    # Just doing a .update wouldn't merge the sub dictionaries.
    _env_additions[platform].update(d)


def get_reload_information():
    try:
        env_additions = _env_additions[sys.platform[:5]]
    except KeyError:
        raise RuntimeError("libfaketime does not support platform %s" % sys.platform)

    needs_reload = True
    if len(set(env_additions) & set(os.environ)) == len(env_additions):
        needs_reload = False

    return needs_reload, env_additions


def reexec_if_needed(remove_vars=True):
    needs_reload, env_additions = get_reload_information()
    if needs_reload:
        new_environ = os.environ.copy()
        new_environ.update(env_additions)
        args = [sys.executable, [sys.executable] + sys.argv, new_environ]
        print 're-exec with libfaketime dependencies'
        os.execve(*args)

    if remove_vars:
        for key in env_additions:
            if key in os.environ:
                del os.environ[key]


class fake_time(ContextDecorator):
    def __init__(self, datetime_spec, only_main_thread=True):
        self.only_main_thread = only_main_thread

        _datetime = datetime_spec
        if isinstance(datetime_spec, basestring):
            _datetime = dateutil.parser.parse(datetime_spec)

        self.time_to_freeze = _datetime  # freezegun compatibility
        self.libfaketime_spec = _datetime.strftime('%Y-%m-%d %T %f')

    def _should_fake(self):
        return self.only_main_thread and threading.current_thread().name == 'MainThread'

    def __enter__(self):
        if self._should_fake():
            self._prev_spec = os.environ.get('FAKETIME')
            os.environ['FAKETIME'] = self.libfaketime_spec

        return self

    def __exit__(self, *exc):
        if self._should_fake():
            if self._prev_spec is not None:
                os.environ['FAKETIME'] = self._prev_spec
            else:
                del os.environ['FAKETIME']

        return False

    # Freezegun compatibility.
    start = __enter__
    stop = __exit__

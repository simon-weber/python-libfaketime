import os
import sys

from contextdecorator import ContextDecorator
import dateutil.parser


def _get_shared_lib(basename):
    return os.path.join(
        os.path.dirname(__file__),
        os.path.join('..', 'vendor', 'libfaketime', 'src'),
        basename)


def _get_env_additions():
    env_additions = {}
    if sys.platform == "linux" or sys.platform == "linux2":
        env_additions['LD_PRELOAD'] = _get_shared_lib('libfaketime.so.1')
    elif sys.platform == "darwin":
        env_additions['DYLD_INSERT_LIBRARIES'] = _get_shared_lib('libfaketime.1.dylib')
        env_additions['DYLD_FORCE_FLAT_NAMESPACE'] = '1'
    else:
        raise RuntimeError("libfaketime does not support platform %s" % sys.platform)

    needs_reload = True
    if len(set(env_additions) & set(os.environ)) == len(env_additions):
        needs_reload = False

    return needs_reload, env_additions


needs_reload, env_additions = _get_env_additions()
if needs_reload:
    os.environ.update(env_additions)
    args = [sys.executable, [sys.executable] + sys.argv, os.environ]
    print 're-exec with libfaketime dependencies'
    os.execve(*args)


class fake_time(ContextDecorator):
    def __init__(self, datetime_spec):
        _datetime = datetime_spec
        if isinstance(datetime_spec, basestring):
            _datetime = dateutil.parser.parse(datetime_spec)

        self.libfaketime_spec = _datetime.strftime('%Y-%m-%d %T')

    def __enter__(self):
        self.prev_spec = os.environ.get('FAKETIME')
        os.environ['FAKETIME'] = self.libfaketime_spec
        return self

    def __exit__(self, *exc):
        if self.prev_spec is not None:
            os.environ['FAKETIME'] = self.prev_spec
        else:
            del os.environ['FAKETIME']

        return False

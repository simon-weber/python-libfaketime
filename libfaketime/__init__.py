import os
import sys


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


def fake_time(datetime_spec):
    def _fake_time_decorator(f):
        def _fake_time_wrapper(*args, **kwargs):
            os.environ['FAKETIME'] = datetime_spec
            res = f(*args, **kwargs)
            os.environ['FAKETIME'] = ''
            return res
        return _fake_time_wrapper
    return _fake_time_decorator

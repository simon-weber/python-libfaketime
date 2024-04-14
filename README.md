python-libfaketime: fast date/time mocking
==========================================

[![github actions](https://github.com/simon-weber/python-libfaketime/actions/workflows/main.yml/badge.svg)](https://github.com/simon-weber/python-libfaketime/actions)
[![pypi](https://img.shields.io/pypi/v/libfaketime.svg)](https://pypi.python.org/pypi/libfaketime)
[![repominder](https://img.shields.io/badge/dynamic/json.svg?label=release&query=%24.status&maxAge=43200&uri=https%3A%2F%2Fwww.repominder.com%2Fbadge%2FeyJmdWxsX25hbWUiOiAic2ltb24td2ViZXIvcHl0aG9uLWxpYmZha2V0aW1lIn0%3D%2F&link=https%3A%2F%2Fwww.repominder.com%2F)](https://www.repominder.com)

python-libfaketime is a wrapper of [libfaketime](https://github.com/wolfcw/libfaketime) for python.
Some brief details:

* Linux and OS X, Pythons 3.8 through 3.12, pypy and pypy3
* Mostly compatible with [freezegun](https://github.com/spulec/freezegun).
* Microsecond resolution.
* Accepts datetimes and strings that can be parsed by dateutil.
* Not threadsafe.
* Will break profiling. A workaround: use ``libfaketime.{begin, end}_callback`` to disable/enable your profiler ([nosetest example](https://gist.github.com/simon-weber/8d43e33448684f85718417ce1a072bc8)).


Installation
------------

```sh
$ pip install libfaketime
```

Usage
-----

```python
import datetime
from libfaketime import fake_time, reexec_if_needed

# libfaketime needs to be preloaded by the dynamic linker.
# This will exec the same command, but with the proper environment variables set.
# You can also skip this and manually manage your env (see "How to avoid re-exec").
reexec_if_needed()

def test_datetime_now():

    # fake_time can be used as a context_manager
    with fake_time('1970-01-01 00:00:01'):

        # Every calls to a date or datetime function returns the mocked date
        assert datetime.datetime.utcnow() == datetime.datetime(1970, 1, 1, 0, 0, 1)
        assert datetime.datetime.now() == datetime.datetime(1970, 1, 1, 0, 0, 1)
        assert time.time() == 1


# fake_time can also be used as a decorator
@fake_time('1970-01-01 00:00:01', tz_offset=12)
def test_datetime_now_with_offset():

    # datetime.utcnow returns the mocked datetime without offset
    assert datetime.datetime.utcnow() == datetime.datetime(1970, 1, 1, 0, 0, 1)

    # datetime.now returns the mocked datetime with the offset passed to fake_time
    assert datetime.datetime.now() == datetime.datetime(1970, 1, 1, 12, 0, 1)
```

### remove_vars

By default, ``reexec_if_needed`` removes the ``LD_PRELOAD`` variable after the
re-execution, to keep your environment as clean as possible. You might want it
to stick around, for example when using parallelized tests that use subprocess
like ``pytest-xdist``, and simply for tests where subprocess is called. To
keep them around, pass ``remove_vars=False`` like:

```python
reexec_if_needed(remove_vars=False)
```

### quiet

To avoid displaying the informative text when re-executing, you can set the
`quiet` parameter:

```python
reexec_if_needed(quiet=True)
```

Performance
-----------

libfaketime tends to be significantly faster than [freezegun](https://github.com/spulec/freezegun).
Here's the output of a [totally unscientific benchmark](https://github.com/simon-weber/python-libfaketime/blob/master/benchmark.py) on my laptop:

```sh
$ python benchmark.py
re-exec with libfaketime dependencies
timing 1000 executions of <class 'libfaketime.fake_time'>
0.021755 seconds

$ python benchmark.py freezegun
timing 1000 executions of <function freeze_time at 0x10aaa1140>
6.561472 seconds
```

Use with py.test
----------------

The [pytest-libfaketime](https://github.com/pytest-dev/pytest-libfaketime) plugin will automatically configure python-libfaketime for you:

```sh
$ pip install pytest-libfaketime
```

Alternatively, you can reexec manually from inside the pytest_configure hook:

```python
# conftest.py
import os
import libfaketime

def pytest_configure():
    libfaketime.reexec_if_needed()
    _, env_additions = libfaketime.get_reload_information()
    os.environ.update(env_additions)
```

Use with tox
------------

In your tox configuration file, under the ``testenv`` bloc, add the libfaketime environment variables to avoid re-execution:

```ini
setenv =
    LD_PRELOAD = {envsitepackagesdir}/libfaketime/vendor/libfaketime/src/libfaketime.so.1
    DONT_FAKE_MONOTONIC = 1
    FAKETIME_DID_REEXEC = true
```

Migration from freezegun
------------------------

python-libfaketime should have the same behavior as freezegun when running on supported code. To migrate to it, you can run:

```bash
find . -type f -name "*.py" -exec sed -i 's/freezegun/libfaketime/g' "{}" \;
```

How to avoid re-exec
--------------------

In some cases - especially when your tests start other processes - re-execing can cause unexpected problems. To avoid this, you can preload the necessary environment variables yourself. The necessary environment for your system can be found by running ``python-libfaketime`` on the command line:

```sh
$ python-libfaketime
export LD_PRELOAD="/home/foo/<snip>/vendor/libfaketime/src/libfaketime.so.1"
export DONT_FAKE_MONOTONIC="1"
export FAKETIME_NO_CACHE="1"
export FAKETIME_DID_REEXEC=true
```

You can easily put this in a script like:

```sh
$ eval $(python-libfaketime)
$ pytest  # ...or any other code that imports libfaketime
```

Contributing and testing
------------------------

Contributions are welcome! You should compile libfaketime before running tests:

```bash
git submodule init --update
git apply --directory libfaketime/vendor/libfaketime libfaketime/vendor/libfaketime.patch
make -C libfaketime/vendor/libfaketime
```

Then you can install requirements with ``pip install -r requirements.txt`` and use ``pytest`` and ``tox`` to run the tests.

uuid1 deadlock
--------------

Calling ``uuid.uuid1()`` multiple times while in a fake_time context can result in a deadlock when an OS-level uuid library is available.
To avoid this, python-libtaketime will monkeypatch uuid._uuid_generate_time (or similar, it varies by version) to None inside a fake_time context.
This may slow down uuid1 generation but should not affect correctness.

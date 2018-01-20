python-libfaketime: fast date/time mocking
==========================================

.. image:: https://img.shields.io/travis/simon-weber/python-libfaketime.svg
        :target: https://travis-ci.org/simon-weber/python-libfaketime

.. image:: https://img.shields.io/pypi/v/libfaketime.svg
        :target: https://pypi.python.org/pypi/libfaketime

python-libfaketime is a wrapper of `libfaketime <https://github.com/wolfcw/libfaketime>`__ for python.
Some brief details:

* Linux and OS X, Pythons 2.7, 3.4, 3.5, 3.6.
* Mostly compatible with `freezegun <https://github.com/spulec/freezegun>`__.
* Microsecond resolution.
* Accepts datetimes and strings that can be parsed by dateutil.
* Not threadsafe.
* Will break profiling. A workaround: use ``libfaketime.{begin, end}_callback`` to disable/enable your profiler (`nosetest example <https://gist.github.com/simon-weber/8d43e33448684f85718417ce1a072bc8>`__).


Installation
------------

.. code-block:: sh

    $ pip install libfaketime

Usage
-----

.. code-block:: python

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


Performance
-----------

libfaketime tends to be significantly faster than `freezegun <https://github.com/spulec/freezegun>`__.
Here's the output of a `totally unscientific benchmark <https://github.com/simon-weber/python-libfaketime/blob/master/benchmark.py>`__ on my laptop:

.. code-block:: sh

    $ python benchmark.py
    re-exec with libfaketime dependencies
    timing 1000 executions of <class 'libfaketime.fake_time'>
    0.021755 seconds

    $ python benchmark.py freezegun
    timing 1000 executions of <function freeze_time at 0x10aaa1140>
    6.561472 seconds


Use with py.test
----------------

The `pytest-libfaketime <https://github.com/azmeuk/pytest-libfaketime>`__ plugin will automatically configure python-libfaketime for you:

.. code-block:: sh

    $ pip install pytest-libfaketime


Alternatively, you can reexec manually from inside the pytest_configure hook:

.. code-block:: python

    # conftest.py
    import os
    import libfaketime

    def pytest_configure():
        libfaketime.reexec_if_needed()
        _, env_additions = libfaketime.get_reload_information()
        os.environ.update(env_additions)

Migration from freezegun
------------------------

python-libfaketime should have the same behavior as freezegun when running on supported code. To migrate to it, you can run:

.. code-block:: bash

    find . -type f -name "*.py" -exec sed -i 's/freezegun/libfaketime/g' "{}" \;


How to avoid re-exec
--------------------

In some cases - especially when your tests start other processes - re-execing can cause unexpected problems. To avoid this, you can preload the necessary environment variables yourself. The necessary environment for your system can be found by running ``python-libfaketime`` on the command line:

.. code-block:: sh

    $ python-libfaketime
    export LD_PRELOAD="/home/foo/<snip>/vendor/libfaketime/src/libfaketime.so.1"
    export FAKETIME_DID_REEXEC=true

You can easily put this in a script like:

.. code-block:: sh

    $ eval $(python-libfaketime)
    $ pytest  # ...or any other code that imports libfaketime


Contributing and testing
------------------------

Contributions are welcome! You should compile libfaketime before running tests:

.. code-block:: bash

    make -C libfaketime/vendor/libfaketime

Then you can install requirements with ``pip install -r requirements.txt`` and use ``pytest`` and ``tox`` to run the tests.

Known Issues
------------

It was found that calling ``uuid.uuid1()`` multiple times while in a fake_time context could result in a deadlock. This situation only occured for users with
a system level uuid1 library. In order to combat this issue, python-libfaketime temporarily disables the system level library by patching
`_uuid_generate_time to None <https://github.com/python/cpython/blob/a1786b287598baa4a9146c9938c9a667bd98fc00/Lib/uuid.py#L565-L570>`_ while in
the fake_time context.

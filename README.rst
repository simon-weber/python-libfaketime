python-libfaketime: fast date/time mocking
==========================================

.. image:: https://img.shields.io/travis/simon-weber/python-libfaketime.svg
        :target: https://travis-ci.org/simon-weber/python-libfaketime

.. image:: https://img.shields.io/pypi/v/libfaketime.svg
        :target: https://pypi.python.org/pypi/libfaketime

python-libfaketime is a wrapper of `libfaketime <https://github.com/wolfcw/libfaketime>`__ for python.
It serves as a fast drop-in replacement for `freezegun <https://github.com/spulec/freezegun>`__.


Installation
------------

Install with **pip**:

.. code-block:: sh

    $ pip install libfaketime


Requirements
------------

Some brief details:

* Works with Linux and OS X, Pythons 2 and 3.
* Microsecond resolution.
* Accepts datetimes and strings that can be parsed by dateutil.
* Not threadsafe.
* Breaks profiling. To workaround this, use ``libfaketime.{begin, end}_callback`` to disable/enable your profiler.


Usage
-----

.. code-block:: python

    import datetime

    from libfaketime import fake_time, reexec_if_needed

    # libfaketime needs to be preloaded by the dynamic linker.
    # This will exec the same command, but with the proper environment variables set.
    # You can also skip this and manually manage your env (see "How to avoid re-exec").
    reexec_if_needed()

    def get_tomorrow():
        return datetime.date.today() + datetime.timedelta(days=1)


    @fake_time('2014-01-01 00:00:00')
    def test_get_tomorrow():
        assert get_tomorrow() == datetime.date(2014, 1, 2)


By default, ``reexec_if_needed`` removes the ``LD_PRELOAD`` variable after the
re-execution, to keep your environment as clean as possible. You might want it
to stick around, for example when using parallelized tests that use subprocess
like ``pytest-xdist``. To keep them around, pass ``remove_vars=False`` like:

.. code-block:: python

    reexec_if_needed(remove_vars=False)


Benchmark against freezegun
---------------------------

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

It's easiest to reexec from inside the pytest_configure hook:

.. code-block:: python

    # conftest.py
    from libfaketime import reexec_if_needed

    def pytest_configure():
        reexec_if_needed()


How to avoid re-exec
--------------------

Sometimes, re-exec does unexpected things. You can avoid those problems by preloading libfaketime yourself. The environment variables you need
can be found by running `python-libfaketime` on the command line:

.. code-block:: sh

    $ python-libfaketime
    export LD_PRELOAD="/home/foo/<snip>/vendor/libfaketime/src/libfaketime.so.1"
    export FAKETIME_DID_REEXEC=true

You can use them as such:

.. code-block:: sh

    $ eval $(python-libfaketime)
    $ nosetests  # ...or any other code that imports libfaketime

Known Issues
------------

It was found that calling `uuid.uuid1()` multiple times while in a fake_time context could result in a deadlock. This situation only occured for users with
a system level uuid1 library. In order to combat this issue, python-libfaketime temporarily disables the system level library by patching
`_uuid_generate_time to None <https://github.com/python/cpython/blob/a1786b287598baa4a9146c9938c9a667bd98fc00/Lib/uuid.py#L565-L570>`_ while in
the fake_time context.

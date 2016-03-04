python-libfaketime: fast date/time mocking
==========================================

python-libfaketime is a wrapper of `libfaketime <https://github.com/wolfcw/libfaketime>`__ for python.

.. code-block:: python

    import datetime

    from libfaketime import fake_time, reexec_if_needed

    # libfaketime needs to be preloaded by the dynamic linker.
    # This will exec the same command, but with the proper environment variables set.
    # Or you can skip running this and manually manage your env (see get_reload_information()).
    reexec_if_needed()

    def get_tomorrow():
        return datetime.date.today() + datetime.timedelta(days=1)


    @fake_time('2014-01-01 00:00:00')
    def test_get_tomorrow():
        assert get_tomorrow() == datetime.date(2014, 1, 2)
 

It serves as a fast drop-in replacement for `freezegun <https://github.com/spulec/freezegun>`__.
Here's the output of a `totally unscientific benchmark <https://github.com/simon-weber/python-libfaketime/blob/master/benchmark.py>`__ on my laptop::

    $ python benchmark.py
    re-exec with libfaketime dependencies
    timing 1000 executions of <class 'libfaketime.fake_time'>
    0.021755 seconds

    $ python benchmark.py freezegun
    timing 1000 executions of <function freeze_time at 0x10aaa1140>
    6.561472 seconds


Some brief details:

* linux and osx
* microsecond resolution
* accepts datetimes and strings that can be parsed by dateutil
* not threadsafe
* will break profiling. A workaround: use ``libfaketime.{begin, end}_callback`` to disable/enable your profiler.
        

To install: ``pip install libfaketime``.


How to avoid re-exec
====================

Sometimes, re-exec does unexpected things. You can avoid those problems by preloading `libfaketime` yourself. The environment variables you need
can be found by running `python-libfaketime` on the command line::

    $ python-libfaketime 
    export LD_PRELOAD="/home/allard/.virtualenvs/libfaketime/local/lib/python2.7/site-packages/libfaketime/vendor/libfaketime/src/libfaketime.so.1"
    export FAKETIME_DID_REEXEC=true

You can use them as such::

    eval $(python-libfaketime)
    nosetests  # for example


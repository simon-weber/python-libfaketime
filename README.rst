libfaketime-tz-wrapper: libfaketime wrapper introducing timezone-awareness.
===========================================================================

A wrapper around `python-libfaketime <https://github.com/simon-weber/python-libfaketime>`__
that introduces awareness for (django) timezones.


Installation
------------

Install with **pip**:

.. code-block:: sh

    $ pip install libfaketime-tz-wrapper


Setup
-----

libfaketime needs the LD_PRELOAD variable to be set.

If you run your tests in PyCharm, add it to the environment variables of your test configuration in PyCharm:
.. code-block::

    name: LD_PRELOAD
    value: /home/foo/<snip>/vendor/libfaketime/src/libfaketime.so.1

If you run tests in the command line, export this environment variable when running the test command:
.. code-block:: sh

    $ LD_PRELOAD="/home/foo/<snip>/vendor/libfaketime/src/libfaketime.so.1" <run test command>

In both cases, replace the <snip> part with the correct path to where the libfaketime package was installed.


Usage
-----

.. code-block:: python

    import datetime

    from libfaketime import fake_time

    def get_tomorrow():
        return datetime.date.today() + datetime.timedelta(days=1)


    @fake_time('2014-01-01 00:00:00')
    def test_get_tomorrow():
        assert get_tomorrow() == datetime.date(2014, 1, 2)

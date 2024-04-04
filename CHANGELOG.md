Changelog
=========

[Semantic versioning](http://semver.org/) is used.

2.0.0
-----
released 2020-04-17

- breaking: drop python 2.7 support
- set LD_LIBRARY_PATH on linux to support paths containing spaces: [#57](https://github.com/simon-weber/python-libfaketime/pull/57)
- fix compatibility with non-pytz tzinfo objects: [#58](https://github.com/simon-weber/python-libfaketime/pull/58)

1.2.1
-----
released 2019-01-20

- fix a deadlock on python 3.7+

1.2.0
-----
released 2018-10-28

- offset-aware datetimes now properly fake the timezone as well: [#49](https://github.com/simon-weber/python-libfaketime/pull/49)

1.1.0
-----
released 2018-10-07

- decorated classes can access the fake_time object with ``self._faked_time``: [#47](https://github.com/simon-weber/python-libfaketime/pull/47)

1.0.0
-----
released 2018-06-16

- **backwards incompatible**: the monotonic clock is no longer mocked: [#45](https://github.com/simon-weber/python-libfaketime/pull/45)
- ensure TZ is set to a valid timezone: [#46](https://github.com/simon-weber/python-libfaketime/pull/46)

0.5.2
-----
released 2018-05-19

- fix a bug causing incorrect times after unpatching under python 3.6+: [#43](https://github.com/simon-weber/python-libfaketime/pull/43)
- fix compilation under gcc8: [#44](https://github.com/simon-weber/python-libfaketime/pull/44)

0.5.1
-----
released 2018-01-19

- fix usage as a class decorator : [#41](https://github.com/simon-weber/python-libfaketime/pull/41)

0.5.0
-----
released 2017-09-10

- alias fake_time for freeze_time: [#31](https://github.com/simon-weber/python-libfaketime/pull/31)
- add tz_offset parameter: [#36](https://github.com/simon-weber/python-libfaketime/pull/36)

0.4.4
-----
released 2017-07-16

- allow contextlib2 as an alternative to contextdecorator: [#30](https://github.com/simon-weber/python-libfaketime/pull/30)

0.4.3
-----
released 2017-07-07

- add macOS Sierra compatibility: [#29](https://github.com/simon-weber/python-libfaketime/pull/29)

0.4.2
-----
released 2016-06-30

- fix only_main_thread=False: [#24](https://github.com/simon-weber/python-libfaketime/pull/24)

0.4.1
-----
released 2016-05-02

- fix deadlocks from uuid.uuid1 when faking time: [#14](https://github.com/simon-weber/python-libfaketime/pull/14)
- remove contextdecorator dependency on python3: [#15](https://github.com/simon-weber/python-libfaketime/pull/15)

0.4.0
-----
released 2016-04-02

- freezegun's tick() is now supported; see [their docs](https://github.com/spulec/freezegun/blob/f1f5148720dd715cfd6dc03bf1861dbedfaad493/README.rst#manual-ticks) for usage.

0.3.0
-----
released 2016-03-04

- invoking ``libfaketime`` from the command line will now print the necessary environment to avoid a re-exec.

0.2.1
-----
released 2016-03-01

- python 3 support

0.1.1
-----
released 2015-09-11

- prevent distribution of test directory: https://github.com/simon-weber/python-libfaketime/pull/4

0.1.0
-----
released 2015-06-23

- add global start/stop callbacks

0.0.3
-----
released 2015-03-28

- initial packaged release

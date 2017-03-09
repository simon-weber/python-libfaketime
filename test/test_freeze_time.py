import datetime
from dateutil.tz import tzutc
from libfaketime import freeze_time
from test import BaseFaketimeTest


class TestFreezeTime(BaseFaketimeTest):
    @freeze_time('2000-01-01 10:00:05')
    def test_freeze_time_parses_easy_strings_as_utc(self):
        self.assertEqual(datetime.datetime.now(tz=tzutc()), datetime.datetime(2000, 1, 1, 10, 0, 5, tzinfo=tzutc()))

    @freeze_time('2000-01-01 10:00:05+0100')
    def test_freeze_time_honors_given_timezone(self):
        self.assertEqual(datetime.datetime.now(tz=tzutc()), datetime.datetime(2000, 1, 1, 9, 0, 5, tzinfo=tzutc()))

    @freeze_time('march 1st, 2014 at 1:59pm')
    def test_freeze_time_parses_tough_strings_as_utc(self):
        self.assertEqual(datetime.datetime.now(tz=tzutc()), datetime.datetime(2014, 3, 1, 13, 59, tzinfo=tzutc()))

    @freeze_time('7 Jul 2015 00:00:00 -0700')
    def test_freeze_time_parses_tough_strings_with_timezone(self):
        self.assertEqual(datetime.datetime.now(tz=tzutc()), datetime.datetime(2015, 7, 7, 7, 0, tzinfo=tzutc()))

    @freeze_time(datetime.datetime(2014, 1, 1, microsecond=123456, tzinfo=tzutc()))
    def test_freeze_time_has_microsecond_granularity(self):
        self.assertEqual(datetime.datetime.now(tz=tzutc()), datetime.datetime(2014, 1, 1, microsecond=123456, tzinfo=tzutc()))

    def test_nested_freeze_time(self):
        self._assert_time_not_faked()

        with freeze_time('1/1/2000'):
            self.assertEqual(datetime.datetime.now(tz=tzutc()), datetime.datetime(2000, 1, 1, tzinfo=tzutc()))

            with freeze_time('1/1/2001',):
                self.assertEqual(datetime.datetime.now(tz=tzutc()), datetime.datetime(2001, 1, 1, tzinfo=tzutc()))

            self.assertEqual(datetime.datetime.now(tz=tzutc()), datetime.datetime(2000, 1, 1, tzinfo=tzutc()))

        self._assert_time_not_faked()

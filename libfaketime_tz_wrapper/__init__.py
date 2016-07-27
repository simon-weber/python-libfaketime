from __future__ import print_function

import dateutil.parser
from datetime import datetime

from django.utils import timezone
import libfaketime


class fake_time(libfaketime.fake_time):
    def __init__(self, datetime_spec, *args, **kwargs):
        datetime_spec = self._prepare(datetime_spec)
        super(fake_time, self).__init__(datetime_spec, *args, **kwargs)

    def _prepare(self, spec):
        dt = spec if isinstance(spec, datetime) else dateutil.parser.parse(spec)

        if timezone.is_aware(dt):
            return timezone.make_naive(dt)
        else:
            return dt

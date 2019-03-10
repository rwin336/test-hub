import datetime
from pytz import timezone

def add_utc_timezone(ct):
    tz = timezone('UTC')
    return datetime.datetime(ct.year, ct.month, ct.day,
                             ct.hour, ct.minute, ct.second,
                             ct.microsecond, tzinfo=tz)


import pytz
import datetime

DT_FRMT = '%Y-%m-%dT%H:%M:%SZ'

class TimeUtils:

    @staticmethod
    def get_dt(time_zone, str_dt, flag_set_minute=True):
        tz_local = pytz.timezone(time_zone)

        if str_dt == 'now':
            dt = datetime.datetime.now()
        elif str_dt == 'now_s00':
            dt = datetime.datetime.now()
            dt = dt.replace(second=0, microsecond=0)
        else:
            dt = datetime.datetime.strptime(str_dt, DT_FRMT)
        dt = tz_local.localize(dt)
        dt_utc = dt.astimezone(pytz.utc)

        if flag_set_minute is True:
            # Set the correct minute (0,15,30,45)
            return TimeUtils.set_start_minute(dt_utc)
        else:
            return dt_utc

    @staticmethod
    def set_start_minute(dt_utc):
        if 0 <= dt_utc.minute < 15:
            return dt_utc.replace(minute=0, second=0, microsecond=0)
        elif 15 <= dt_utc.minute < 30:
            return dt_utc.replace(minute=15, second=0, microsecond=0)
        elif 30 <= dt_utc.minute < 45:
            return dt_utc.replace(minute=30, second=0, microsecond=0)
        else:
            return dt_utc.replace(minute=45, second=0, microsecond=0)

    @staticmethod
    def get_end_dt(dt_start, duration):

        if duration[-1] == 'm':
            dt_end = dt_start + datetime.timedelta(minutes=int(duration[0:-1]))
        elif duration[-1] == 'h':
            dt_end = dt_start + datetime.timedelta(hours=int(duration[0:-1]))
        elif duration[-1] == 'd':
            dt_end = dt_start + datetime.timedelta(days=int(duration[0:-1]))
        return dt_end

    @staticmethod
    def calc_period_starting(dt_end, period):
        if period[-1] == 'm':
            dt_start = dt_end - datetime.timedelta(minutes=int(period[0:-1]))
        elif period[-1] == 'h':
            dt_start = dt_end - datetime.timedelta(hours=int(period[0:-1]))
        elif period[-1] == 'd':
            dt_start = dt_end - datetime.timedelta(days=int(period[0:-1]))

        return dt_start

    @staticmethod
    def get_start_end(duration, time_zone, back=False):
        dt_start = TimeUtils.get_dt(time_zone, 'now_s00', flag_set_minute=False)

        offset = 0
        if duration[-1] == 'm':
            if back is True:
                dt_end = dt_start - datetime.timedelta(minutes=int(duration[0:-1]))
                offset = int(duration[0:-1]) * 60
            else:
                dt_end = dt_start + datetime.timedelta(minutes=int(duration[0:-1]))

        elif duration['duration'][-1] == 'h':
            if back is True:
                dt_end = dt_start - datetime.timedelta(hours=int(duration[0:-1]))
            else:
                dt_end = dt_start + datetime.timedelta(hours=int(duration[0:-1]))
                offset = int(duration[0:-1]) * 60 * 60

        elif duration['duration'][-1] == 'd':
            if back is True:
                dt_end = dt_start - datetime.timedelta(days=int(duration[0:-1]))
            else:
                dt_end = dt_start + datetime.timedelta(days=int(duration[0:-1]))
                offset = int(duration[0:-1]) * 60 * 60 * 24

        if back is True:
            return dt_end, dt_start, offset
        else:
            return dt_start, dt_end, offset
import datetime
from influxdb import InfluxDBClient
from classes.time_utils import TimeUtils


class InfluxDBInterface():

    """ Class and methods to interact with a InfluxDB database
    """

    def __init__(self, cfg, logger):

        self.cfg = cfg
        logger.info('Connection to InfluxDb server on socket [%s:%s]' % (cfg['influxDB']['host'],
                                                                         cfg['influxDB']['port']))
        try:
            self.influx_client = InfluxDBClient(
                                                    host=cfg['influxDB']['host'],
                                                    port=cfg['influxDB']['port'],
                                                    password=cfg['influxDB']['password'],
                                                    username=cfg['influxDB']['user'],
                                                    database=cfg['influxDB']['db'],
                                                    ssl=cfg['influxDB']['ssl']
                                                )
        except Exception as e:
            logger.error('EXCEPTION: %s' % str(e))
            self.influx_client = None

        self.logger = logger

    def get_random_key(self, meter, dt_utc):
        str_query = 'SELECT value FROM random_keys WHERE meter=\'m_%s\' AND time=\'%s\'' % (meter,
                                                                                            dt_utc.strftime(self.DT_FRMT))

        try:
            result = self.influxdb_client.query(str_query)
            return result.raw['series'][0]['values'][0][1]
        except Exception as e:
            self.logger.info('Random key not available in InfluxDB')
            return None

    def get_single_value(self, signal, start, end):
        query = 'SELECT mean("value") FROM data WHERE signal=\'%s\' AND time>=\'%s\' and time<\'%s\'' % (signal,
                                                                                                         start,
                                                                                                         end)
        self.logger.info('Query: %s' % query)
        try:
            result = self.influx_client.query(query)
            return result.raw['series'][0]['values'][0][1]
        except Exception as e:
            self.logger.error('EXCEPTION: %s' % str(e))
            return 0

    def get_dataset(self, signal, end_dt):
        if 'minutesGrouping' not in self.cfg['utils'].keys():
            minutes_back = 15
        else:
            minutes_back = self.cfg['utils']['minutesGrouping']

        DT_FRMT = '%Y-%m-%dT%H:%M:%SZ'
        start_str_dt = datetime.datetime.strftime(end_dt-datetime.timedelta(minutes=minutes_back), DT_FRMT)
        end_str_dt = datetime.datetime.strftime(end_dt, DT_FRMT)
        return self.get_single_value(signal, start_str_dt, end_str_dt)


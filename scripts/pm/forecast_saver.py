# Importing section
import datetime
import json
import requests
import argparse
import logging
import time
from classes.time_utils import TimeUtils
from classes.influxdb_interface import InfluxDBInterface
from classes.market_engine import MarketEngine

# Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='config file')
    arg_parser.add_argument('-l', help='log file')

    args = arg_parser.parse_args()
    cfg = json.loads(open(args.c).read())

    # Get configuration about connections to InfluxDB and remote service related to data retrieving
    tmp_config = json.loads(open(cfg['connectionsFile']).read())
    cfg.update(tmp_config)

    # set logging object
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not args.l:
        log_file = None
    else:
        log_file = args.l

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(threadName)s::%(levelname)s::%(funcName)s::%(message)s',
                        level=logging.INFO, filename=log_file)

    url_prefix = cfg['sidechainRestApi']
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    logger.info('Starting program')

    influxdb_interface = InfluxDBInterface(cfg=cfg, logger=logger)
    dt_end_utc = TimeUtils.get_dt(cfg['utils']['timeZone'], 'now_s00', flag_set_minute=False)
    dt_end_utc = dt_end_utc - datetime.timedelta(minutes=cfg['shiftBackMinutes']['forecastSaving'])

    r = requests.get('%s/account' % url_prefix, headers=headers)
    player_data = json.loads(r.text)

    # Define the timestamp that will be the same for all the signals
    now = datetime.datetime.now()
    dt = now.replace(second=0)
    dt = dt - datetime.timedelta(minutes=cfg['shiftBackMinutes']['forecastSaving'])
    ts = int(dt.timestamp())

    me = MarketEngine(cfg, logger)
    persistence_power_imp = influxdb_interface.get_15m_past_measurements('PImp',  dt_end_utc)
    persistence_power_exp = influxdb_interface.get_15m_past_measurements('PExp',  dt_end_utc)

    # Calculate the values
    values = []
    for i in range(0, cfg['forecast']['steps']):
        values.append('%s,%s' % (int(persistence_power_imp[i][1]), int(persistence_power_exp[i][1])))
    params = {
                'ts': ts,
                'player': player_data['name'],
                'values': values
             }

    if me.get_forecast(me.local_account['name']) is None:
        cmd_request = '%s/createForecast' % url_prefix
    else:
        cmd_request = '%s/updateForecast' % url_prefix

    logger.info('Request: %s' % cmd_request)
    logger.info('params: %s' % params)
    r = requests.post(cmd_request, headers=headers, json=params)
    data = json.loads(r.text)
    logger.info('Response: %s' % data)

    # Wait some seconds to be sure that the transaction has been handled
    time.sleep(cfg['utils']['sleepBetweenTransactions'])

    check_tx_url = '%s/checkTx/%s' % (url_prefix, data['tx_hash'])
    logger.info('Check tx: %s' % check_tx_url)
    r = requests.get(check_tx_url)
    data = json.loads(r.text)
    logger.info('Response: %s' % data)

    logger.info('Ending program')

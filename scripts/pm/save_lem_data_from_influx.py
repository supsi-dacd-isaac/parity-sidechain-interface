# Importing section
import datetime
import json
import requests
import argparse
import logging
import time
from classes.influxdb_interface import InfluxDBInterface

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
    end_dt_utc = influxdb_interface.get_dt('now_s00', flag_set_minute=False)
    end_dt_utc = influxdb_interface.get_dt('now', flag_set_minute=False)

    r = requests.get('%s/account' % url_prefix, headers=headers)
    player_data = json.loads(r.text)

    tx_hashes = dict()
    for signal in cfg['signals']:
        value = influxdb_interface.get_dataset(signal, end_dt_utc)

        now = datetime.datetime.now()
        dt = now.replace(second=0)
        params = {
                    'timestamp': int(dt.timestamp()),
                    'signal': signal,
                    'player': player_data['name'],
                    'value': round(float(value), 1),
                    'measureUnit': 'W',
                 }

        cmd_request = '%s/createLemMeasure' % url_prefix
        logger.info('Request: %s' % cmd_request)
        r = requests.post(cmd_request, headers=headers, json=params)
        data = json.loads(r.text)
        logger.info('Response: %s' % data)
        tx_hashes[signal] = data['tx_hash']

        # Wait some seconds to be sure that the transaction has been handled
        time.sleep(8)

    for signal in cfg['signals']:
        check_tx_url = '%s/checkTx/%s' % (url_prefix, tx_hashes[signal])
        logger.info('Check tx: %s' % check_tx_url)
        r = requests.get(check_tx_url)
        data = json.loads(r.text)
        logger.info('Response: %s' % data)

    logger.info('Ending program')

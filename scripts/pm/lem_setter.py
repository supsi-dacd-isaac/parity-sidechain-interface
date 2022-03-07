# Importing section
import http
import json
import requests
import argparse
import logging
import datetime
import time
from classes.time_utils import TimeUtils

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

    # Define start and end datetime
    dt_start = TimeUtils.get_dt(cfg['utils']['timeZone'], 'now_s00', flag_set_minute=False)
    if cfg['lem']['duration'][-1] == 'm':
        dt_end = dt_start + datetime.timedelta(minutes=int(cfg['lem']['duration'][0:-1]))
    elif cfg['lem']['duration'][-1] == 'h':
        dt_end = dt_start + datetime.timedelta(hours=int(cfg['lem']['duration'][0:-1]))
    elif cfg['lem']['duration'][-1] == 'd':
        dt_end = dt_start + datetime.timedelta(days=int(cfg['lem']['duration'][0:-1]))

    dt_start = dt_start - datetime.timedelta(minutes=cfg['shiftBackMinutes']['lemSetting'])
    dt_end = dt_end - datetime.timedelta(minutes=cfg['shiftBackMinutes']['lemSetting'])

    # Get the aggregator
    res = requests.get('%s/aggregator' % cfg['sidechainRestApi'])
    aggregator_id = json.loads(res.text)['Aggregator']['idx']

    params = {
        'start': int(dt_start.timestamp()),
        'end': int(dt_end.timestamp()),
        'aggregator': aggregator_id,
        'state': 'ACTIVE',
        'marketParameters': [0, 0, 0, 0, 0],
        'players': cfg['lem']['players']
    }

    cmd_request = '%s/createLem' % url_prefix
    logger.info('Request: %s' % cmd_request)
    logger.info('Parameters: %s' % params)
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

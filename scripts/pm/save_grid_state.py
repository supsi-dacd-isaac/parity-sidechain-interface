# Importing section
import json
import requests
import argparse
import logging
import time
import numpy as np
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
    dt = influxdb_interface.get_dt('now_s00', flag_set_minute=False)

    # Get the state according to the configured probabilities
    elements = []
    probabilities = []
    for state in cfg['grid']['statesProbabilities'].keys():
        elements.append(state)
        probabilities.append(cfg['grid']['statesProbabilities'][state])

    params = {
                'timestamp': int(dt.timestamp()),
                'grid': cfg['grid']['name'],
                'state': np.random.choice(elements, p=probabilities),
             }

    cmd_request = '%s/createGridState' % url_prefix
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

# Importing section
import datetime
import json
import random
import requests
import argparse
import logging
import time

#  Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-l', help='log file')

    args = arg_parser.parse_args()

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


    url_prefix = 'http://localhost:9119'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    logger.info('Starting program')

    r = requests.get('%s/account' % url_prefix, headers=headers)
    data = json.loads(r.text)

    now = datetime.datetime.now()
    dt = now.replace(second=0)
    params = {
                'timestamp': int(dt.timestamp()),
                'signal': 'P',
                'player': data['name'],
                'value': round(random.uniform(0, 30000)/10, 1),
                'measureUnit': 'W',
             }

    cmd_request = '%s/createLemMeasure' % url_prefix
    logger.info('Request: %s' % cmd_request)
    r = requests.post(cmd_request, headers=headers, json=params)
    data = json.loads(r.text)
    logger.info('Response: %s' % data)

    # Wait some seconds to be sure that the transaction has been handled
    time.sleep(5)

    check_tx_url = '%s/checkTx/%s' % (url_prefix, data['tx_hash'])
    logger.info('Check tx: %s' % check_tx_url)
    r = requests.get(check_tx_url)
    data = json.loads(r.text)
    logger.info('Response: %s' % data)

    logger.info('Ending program')

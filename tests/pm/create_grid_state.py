# Importing section
import json
import requests
import argparse
import datetime
import time

from http import HTTPStatus

#  Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    args = arg_parser.parse_args()

    set_cmd = 'createGridState'
    now = datetime.datetime.now()
    dt = now.replace(second=0)
    params = {
                'timestamp': int(dt.timestamp()),
                'grid': 'aem_lic',
                'state': 'YELLOW',
             }

    cmd_url = 'http://localhost:9119/%s' % set_cmd

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    print('COMMAND: %s' % cmd_url)
    print('PARAMS: %s' % params)

    r = requests.post(cmd_url, headers=headers, json=params)
    data = json.loads(r.text)
    print('RESPONSE: %s\n' % data)

    # Wait some seconds to be sure that the transaction has been handled
    time.sleep(5)

    check_tx_url = 'http://localhost:9119/checkTx/%s' % data['tx_hash']
    print('CHECK TX: %s' % check_tx_url)
    r = requests.get(check_tx_url)

    data = json.loads(r.text)
    print('RESPONSE: %s\n' % data)

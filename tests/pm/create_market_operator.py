# Importing section
import json
import requests
import argparse
import hashlib
import time

from http import HTTPStatus

#  Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    args = arg_parser.parse_args()

    set_cmd = 'createMarketOperator'
    params = {
                # pseudonym
                # 'idx': 'aem',
                'idx': '96bba630b6a8e5e639b87c7ea3ad8802e3f90dee0f966a73c65af65875ef5d18',
                'address': 'cosmos1au65sw4rh40x3u0jmxstkm958wgpaxv2g86qq2'
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

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
    arg_parser.add_argument('-m', help='Ethernet MAC address')
    args = arg_parser.parse_args()

    # Get the identifier
    eth_mac = args.m
    h = hashlib.new('sha512')
    h.update(str.encode(eth_mac))
    real_account = h.hexdigest()

    time.sleep(2)
    cmds = ['getAdmin', 'meterAccount']
    cmds = ['get_tokens_amount']

    for cmd in cmds:
        print('GET COMMAND: %s' % cmds)
        r = requests.get('http://localhost:9119/%s' % cmd)
        print('RESPONSE STATUS %i' % r.status_code)

        if r.status_code == HTTPStatus.OK:
            # print(r.text)
            data = json.loads(r.text)
            print('RESPONSE DATA %s\n' % data)

        time.sleep(2)



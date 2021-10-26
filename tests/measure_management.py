# Importing section
import datetime
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

    set_cmd = 'setMeasure'
    get_cmd = 'getMeasure'

    now = int(datetime.datetime.utcnow().timestamp())
    signal = 'PImp'
    data = {'signal': signal, 'timestamp': '%i' % now, 'value': '250'}

    print('SET COMMAND: %s' % set_cmd)

    r = requests.post('http://localhost:9119/%s' % set_cmd, params=data)
    print('RESPONSE STATUS %i\n' % r.status_code)

    time.sleep(6)

    print('GET COMMAND: %s' % get_cmd)
    r = requests.get('http://localhost:9119/%s?signal=%s&timestamp=%s' % (get_cmd, signal, now))
    print('RESPONSE STATUS %i' % r.status_code)

    if r.status_code == HTTPStatus.OK:
        data = json.loads(r.text)
        print('RESPONSE DATA %s' % data)

    time.sleep(1)

    print('GET COMMAND: %s' % get_cmd)
    r = requests.get('http://localhost:9119/%s?signal=%s&timestamp=%s' % (get_cmd, 'E_cons', now))
    print('RESPONSE STATUS %i' % r.status_code)

    if r.status_code == HTTPStatus.OK:
        data = json.loads(r.text)
        print('RESPONSE DATA %s' % data)



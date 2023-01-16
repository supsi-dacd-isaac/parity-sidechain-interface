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

    set_cmd = 'updatePlayer'
    list_params = [
                        {
                            # pseudonym
                            'idx': 'pros04',
                            'address': 'addr_pros04',
                            'role': 'prosumer'
                        }
                ]

    cmd_url = 'http://localhost:9119/%s' % set_cmd

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    for params in list_params:
        print('COMMAND: %s' % cmd_url)
        print('PARAMS: %s' % params)

        r = requests.post(cmd_url, headers=headers, json=params)
        data = json.loads(r.text)
        print('RESPONSE: %s\n' % data)


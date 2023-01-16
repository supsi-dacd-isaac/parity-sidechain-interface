# Importing section
import json
import requests
import datetime

def send_post(cmd_request, parameters, logger):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    logger.info('Request: %s' % cmd_request)
    logger.info('Parameters: %s' % parameters)
    r = requests.post(cmd_request, headers=headers, json=parameters)
    data = json.loads(r.text)
    logger.info('Response: %s' % data)
    return data


def send_get(cmd_request, logger):
    logger.info('Request: %s' % cmd_request)
    r = requests.get(cmd_request)
    data = json.loads(r.text)
    logger.info('Response: %s' % data)


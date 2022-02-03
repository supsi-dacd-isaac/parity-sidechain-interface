# Importing section
import json
import requests
import datetime


def get_end_dt(dt_start, duration):

    if duration[-1] == 'm':
        dt_end = dt_start + datetime.timedelta(minutes=int(duration[0:-1]))
    elif duration[-1] == 'h':
        dt_end = dt_start + datetime.timedelta(hours=int(duration[0:-1]))
    elif duration[-1] == 'd':
        dt_end = dt_start + datetime.timedelta(days=int(duration[0:-1]))
    return dt_end


def calc_period_starting(dt_end, period):
    if period[-1] == 'm':
        dt_start = dt_end - datetime.timedelta(minutes=int(period[0:-1]))
    elif period[-1] == 'h':
        dt_start = dt_end - datetime.timedelta(hours=int(period[0:-1]))
    elif period[-1] == 'd':
        dt_start = dt_end - datetime.timedelta(days=int(period[0:-1]))

    return dt_start


def get_start_end(duration, influxdb_interface, back=False):
    dt_start = influxdb_interface.get_dt('now_s00', flag_set_minute=False)

    offset = 0
    if duration[-1] == 'm':
        if back is True:
            dt_end = dt_start - datetime.timedelta(minutes=int(duration[0:-1]))
            offset = int(duration[0:-1]) * 60
        else:
            dt_end = dt_start + datetime.timedelta(minutes=int(duration[0:-1]))

    elif duration['duration'][-1] == 'h':
        if back is True:
            dt_end = dt_start - datetime.timedelta(hours=int(duration[0:-1]))
        else:
            dt_end = dt_start + datetime.timedelta(hours=int(duration[0:-1]))
            offset = int(duration[0:-1]) * 60 * 60

    elif duration['duration'][-1] == 'd':
        if back is True:
            dt_end = dt_start - datetime.timedelta(days=int(duration[0:-1]))
        else:
            dt_end = dt_start + datetime.timedelta(days=int(duration[0:-1]))
            offset = int(duration[0:-1]) * 60 * 60 * 24

    if back is True:
        return dt_end, dt_start, offset
    else:
        return dt_start, dt_end, offset


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


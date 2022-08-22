# Importing section
import json
import sys
import urllib3
import requests
import argparse
import logging

from datetime import timezone
import datetime

from influxdb import InfluxDBClient

from classes.pm_sidechain_interface import PMSidechainInterface

urllib3.disable_warnings()

#  Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='configuration file')
    arg_parser.add_argument('-l', help='log file')

    args = arg_parser.parse_args()

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

    # --------------------------------------------------------------------------- #
    # InfluxDB connection
    # --------------------------------------------------------------------------- #
    logger.info('Connection to InfluxDb server on socket [%s:%s]' % (cfg['influxDB']['host'], cfg['influxDB']['port']))
    try:
        influx_client = InfluxDBClient(host=cfg['influxDBDemo']['host'], port=cfg['influxDBDemo']['port'],
                                       password=cfg['influxDBDemo']['password'], username=cfg['influxDBDemo']['user'],
                                       database=cfg['influxDBDemo']['db'], ssl=cfg['influxDBDemo']['ssl'])
    except Exception as e:
        logger.error('EXCEPTION: %s' % str(e))
        sys.exit(3)
    logger.info('Connection successful')

    pmsi = PMSidechainInterface(cfg, logger, True)

    players_idxs, players_addrs = pmsi.get_all_available_prosumers()
    aggregator = pmsi.get_aggregator()
    print(aggregator)

    logger.info('Starting program')

    # Get timestamp
    dt = datetime.datetime.now(timezone.utc)
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_ts = int(utc_time.timestamp())

    dps = []
    for i in range(0, len(players_addrs)):
        # Get single prosumer balance
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        r = requests.get('http://localhost:9119/balances/%s/%s' % (players_addrs[i], cfg['cosmos']['tokenName']), headers=headers)
        data = json.loads(r.text)
        logger.info('PRO[%s - %s]: %s' % (players_idxs[i], players_addrs[i], data['balance']['amount']))

        dps.append(
                    {
                        'time': utc_ts,
                        'measurement': cfg['influxDBDemo']['measurement'],
                        'fields': dict(value=float(data['balance']['amount'])),
                        'tags': dict(address=players_addrs[i], id=players_idxs[i], token=cfg['cosmos']['tokenName'], role='PROS')
                    }
                )

    # Get aggregator balance
    r = requests.get('http://localhost:9119/balances/%s/%s' % (players_addrs[i], cfg['cosmos']['tokenName']), headers=headers)
    data = json.loads(r.text)
    logger.info('AGG[%s - %s]: %s' % (aggregator['idx'], aggregator['address'], data['balance']['amount']))

    dps.append(
                {
                    'time': utc_ts,
                    'measurement': cfg['influxDBDemo']['measurement'],
                    'fields': dict(value=float(data['balance']['amount'])),
                    'tags': dict(address=aggregator['address'], id=aggregator['idx'], token=cfg['cosmos']['tokenName'],
                                 role='AGG')
                }
            )

    logger.info('Send %i points to InfluxDB server' % len(dps))
    influx_client.write_points(dps, time_precision=cfg['influxDBDemo']['timePrecision'])
    logger.info('Ending program')



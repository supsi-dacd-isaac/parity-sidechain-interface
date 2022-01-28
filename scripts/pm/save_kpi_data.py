# Importing section
import datetime
import json
import argparse
import logging
import random
import requests
import time
import utilities as u
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

    r = requests.get('%s/account' % url_prefix, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    player_data = json.loads(r.text)

    logger.info('Starting program')

    for sla in cfg['slas']:
        dt_start, dt_end, offset = u.get_start_end(sla['duration'], InfluxDBInterface(cfg=cfg, logger=logger),
                                                   back=True)

        # Cycle over the configured KPIs
        for kpi in sla['kpis']:
            random.seed(42)

            kpi_value = round(random.uniform(float(kpi['valuesInterval'][0]), float(kpi['valuesInterval'][1])), 2)

            r = requests.get('%s/kpiFeatures/%s_%i-%i' % (url_prefix, kpi['idPrefix'],
                                                          int(dt_start.timestamp())+offset,
                                                          int(dt_end.timestamp())+offset), headers=headers)
            kpi_data = json.loads(r.text)

            params = {
                        'timestamp': int(dt_end.timestamp())+offset,
                        'player': player_data['name'],
                        'kpi': kpi_data['kpiFeatures']['index'],
                        'value': kpi_value,
                        'measureUnit': kpi['mu']
                     }

            u.send_post('%s/createKpiMeasure' % url_prefix, params, logger)
            time.sleep(cfg['utils']['sleepBetweenTransactions'])

    logger.info('Ending program')

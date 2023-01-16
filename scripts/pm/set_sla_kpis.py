# Importing section
import json
import requests
import argparse
import logging
import time
import datetime
from classes.time_utils import TimeUtils

import utilities as u

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

    logger.info('Starting program')

    # Get the aggregator
    res = requests.get('%s/aggregator' % cfg['sidechainRestApi'])
    aggregator_id = json.loads(res.text)['Aggregator']['idx']

    # Cycle over the configured SLAs
    for sla in cfg['slas']:
        dt_start, dt_end, _ = TimeUtils.get_start_end(sla['duration'], cfg['utils']['timeZone'])
        dt_start = dt_start - datetime.timedelta(minutes=cfg['shiftBackMinutes']['kpiSetting'])
        dt_end = dt_end - datetime.timedelta(minutes=cfg['shiftBackMinutes']['kpiSetting'])

        sla_idx = '%s_%i-%i' % (sla['idPrefix'], int(dt_start.timestamp()), int(dt_end.timestamp()))

        params = {
            'idx': sla_idx,
            'start': int(dt_start.timestamp()),
            'end': int(dt_end.timestamp()),
        }

        u.send_post('%s/createSla' % url_prefix, params, logger)
        time.sleep(cfg['utils']['sleepBetweenTransactions'])

        # Cycle over the configured KPIs
        for kpi in sla['kpis']:
            params = {
                'idx': '%s_%i-%i' % (kpi['idPrefix'], int(dt_start.timestamp()), int(dt_end.timestamp())),
                'idxSla': sla_idx,
                'rule': kpi['rule'],
                'limit': kpi['limit'],
                'measureUnit': kpi['mu'],
                'penalty': kpi['penalty'],
                'players': kpi['players'],
            }

            u.send_post('%s/createKpiFeatures' % url_prefix, params, logger)
            time.sleep(cfg['utils']['sleepBetweenTransactions'])

    logger.info('Ending program')

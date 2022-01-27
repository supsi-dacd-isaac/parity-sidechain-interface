# Importing section
import json
import argparse
import logging
from classes.influxdb_interface import InfluxDBInterface
from classes.slakpi_engine import SlaKpiManager

import utilities as u

#  Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='configuration file')
    arg_parser.add_argument('-l', help='log file')

    args = arg_parser.parse_args()

    args = arg_parser.parse_args()
    cfg = json.loads(open(args.c).read())

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

    logger.info('Starting program')

    # Define the start/end timestamps
    influxdb_interface = InfluxDBInterface(cfg=cfg, logger=logger)
    dt_end = influxdb_interface.get_dt('now_s00', flag_set_minute=False)

    skm = SlaKpiManager(cfg, logger)
    skm.set_main_sidechain_nodes_info()

    penalty_amount = {skm.local_account['name']: 0}

    for sla in cfg['slas']:
        dt_start = u.calc_period_starting(dt_end, sla['solutionPeriod'])

        # Cycle over the configured KPIs
        for kpi in sla['kpis']:

            dt_curr = dt_start
            while dt_curr < dt_end:
                dt_kpi_start = dt_curr
                dt_kpi_end = u.get_end_dt(dt_curr, sla['duration'])
                ts_kpi_start = int(dt_kpi_start.timestamp())
                ts_kpi_end = int(dt_kpi_end.timestamp())

                # Go to the next market
                dt_curr = u.get_end_dt(dt_curr, sla['duration'])

                # Get kpi feature
                kpi_feature = skm.get_kpi_features(kpi['idPrefix'], ts_kpi_start, ts_kpi_end)

                # Get kpi value
                kpi_dataset = skm.get_kpi_value(kpi['idPrefix'], skm.local_account['name'], ts_kpi_start, ts_kpi_end)

                # Eventually update the account balance
                penalty = skm.check_value(kpi_feature, kpi_dataset)
                penalty_amount[skm.local_account['name']] -= penalty

                logger.info('KPI %s: value: %s %s; rule: %s; limit: %s %s; '
                            'applied penalty: %i' % (kpi_feature['index'], kpi_dataset['value'],
                                                     kpi_feature['mu'], kpi_feature['rule'],
                                                     kpi_feature['limit'], kpi_feature['mu'], penalty))

    # Eventually move tokens due to KPIs penalties
    logger.info('Total penalty: %s' % abs(penalty_amount[skm.local_account['name']]))
    skm.send_tokens(skm.local_account, skm.dso, abs(penalty_amount[skm.local_account['name']]))

    logger.info('Ending program')

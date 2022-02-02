# Importing section
import datetime
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
    dt_end = dt_end - datetime.timedelta(minutes=cfg['shiftBackMinutes']['slaKpis'])

    skm = SlaKpiManager(cfg, logger)
    skm.set_main_sidechain_nodes_info()

    penalty_amount = {skm.local_account['name']: 0}

    for sla in cfg['slas']:
        dt_start = u.calc_period_starting(dt_end, sla['solutionPeriod'])

        logger.info('SLA analysis -> prefix: %s; period: [%s - %s]' % (sla['idPrefix'],
                                                                       dt_start.strftime('%Y-%m-%d %H:%M'),
                                                                       dt_end.strftime('%Y-%m-%d %H:%M')))

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

                if kpi_feature is not None:
                    # Check if this kpis has to be considered by the current node/prosumer
                    # N.B. the deal node/prosumer is done off-chain, this is an additional checking
                    if skm.local_account['name'] in kpi_feature['players']:
                        # Get kpi value
                        kpi_dataset = skm.get_kpi_value(kpi['idPrefix'], skm.local_account['name'], ts_kpi_start, ts_kpi_end)

                        if kpi_dataset is not None:
                            # Eventually update the account balance
                            penalty = skm.check_value(kpi_feature, kpi_dataset)
                            penalty_amount[skm.local_account['name']] -= penalty

                            logger.info('KPI %s: value: %s %s; rule: %s; limit: %s %s; '
                                        'applied penalty: %i' % (kpi_feature['index'], kpi_dataset['value'],
                                                                 kpi_feature['mu'], kpi_feature['rule'],
                                                                 kpi_feature['limit'], kpi_feature['mu'], penalty))
                        else:
                            logger.warning('KPI dataset %s-%s_%i-%i-%i not available' % (skm.local_account['name'],
                                                                                         kpi['idPrefix'],
                                                                                         ts_kpi_start,
                                                                                         ts_kpi_end,
                                                                                         ts_kpi_end))
                    else:
                        logger.warning('KPI %s (SLA %s) not to be considered by node %s' % (kpi_feature['index'],
                                                                                            kpi_feature['sla'],
                                                                                            skm.local_account['name']))
                else:
                    logger.warning('KPI %s_%i-%i not available' % (kpi['idPrefix'], ts_kpi_start, ts_kpi_end))

    # Eventually move tokens due to KPIs penalties
    logger.info('Total penalty: %s' % abs(penalty_amount[skm.local_account['name']]))
    amount = abs(penalty_amount[skm.local_account['name']])
    if amount > 0:
        skm.send_tokens(skm.dso, abs(penalty_amount[skm.local_account['name']]))

    logger.info('Ending program')

# Importing section
import datetime
import json
import argparse
import logging
from classes.influxdb_interface import InfluxDBInterface
from classes.market_engine import MarketEngine


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

    logger.info('Starting program')

    # Define the start/end timestamps
    influxdb_interface = InfluxDBInterface(cfg=cfg, logger=logger)
    dt_end = influxdb_interface.get_dt('now_s00', flag_set_minute=False)

    # Define the MarketEngine and CosmosInterface instances
    me = MarketEngine(cfg, logger)

    dt_start = calc_period_starting(dt_end, cfg['lem']['solutionPeriod'])

    dt_curr = dt_start

    # Get all the available prosumers
    players_balance = dict()
    for prosumer in me.get_all_available_prosumers():
        players_balance[prosumer] = 0

    while dt_curr < dt_end:
        dt_lem_start = dt_curr
        dt_lem_end = get_end_dt(dt_curr, cfg['lem']['marketsDuration'])
        ts_lem_start = int(dt_lem_start.timestamp())
        ts_lem_end = int(dt_lem_end.timestamp())

        # Go to the next market
        dt_curr = get_end_dt(dt_curr, cfg['lem']['marketsDuration'])

        # Get the grid state
        grid_state = me.get_grid_state(ts_lem_start)

        if grid_state == 'RED':
            logger.error('LEM was in RED state in period [%s - %s]' % (dt_lem_start, dt_lem_end))
        else:
            # Get the prosumers constituting the LEM and the aggregator
            players, aggregator = me.get_lem_features(ts_lem_start, ts_lem_end)

            # Get the market parameters
            lem_parameters = me.get_market_default_parameters()

            # Get the related measures measure
            lem_df = me.get_lem_df(ts_lem_start, players)

            # Solve the market
            players_balance = me.solve_single_lem(players_balance, lem_df, lem_parameters)

    # Finally move tokens
    me.move_tokens(players_balance)

    logger.info('Ending program')

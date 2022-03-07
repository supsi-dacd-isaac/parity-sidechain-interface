# Importing section
import json
import datetime
import argparse
import logging
from classes.time_utils import TimeUtils
from classes.market_engine import MarketEngine

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
    dt_end = TimeUtils.get_dt(cfg['utils']['timeZone'], 'now_s00', flag_set_minute=False)
    dt_end = dt_end - datetime.timedelta(minutes=cfg['shiftBackMinutes']['lemSolving'])

    me = MarketEngine(cfg, logger)
    me.set_main_sidechain_nodes_info()

    dt_start = TimeUtils.calc_period_starting(dt_end, cfg['lem']['solutionPeriod'])

    dt_curr = dt_start

    # Get all the available prosumers
    players_balance = dict()
    for prosumer in me.get_all_available_prosumers():
        players_balance[prosumer] = 0

    while dt_curr < dt_end:
        dt_lem_start = dt_curr
        dt_lem_end = TimeUtils.get_end_dt(dt_curr, cfg['lem']['duration'])
        ts_lem_start = int(dt_lem_start.timestamp())
        ts_lem_end = int(dt_lem_end.timestamp())

        logger.info('LEM analysis -> period: [%s - %s]' % (dt_lem_start.strftime('%Y-%m-%d %H:%M'),
                                                           dt_lem_end.strftime('%Y-%m-%d %H:%M')))

        # Go to the next market
        dt_curr = TimeUtils.get_end_dt(dt_curr, cfg['lem']['duration'])

        # Get the grid state
        grid_state = me.get_grid_state(ts_lem_start)

        if grid_state == me.GRIDSTATE_RED:
            logger.error('LEM was in RED state in period [%s - %s]' % (dt_lem_start, dt_lem_end))
        else:
            # Get the prosumers constituting the LEM and the aggregator
            players, aggregator, tmp_lem_pars = me.get_lem_features(ts_lem_start, ts_lem_end)

            # Check if default market parameters have to be used (i.e. the prices parameters are equal to 0)
            if (tmp_lem_pars[1] == tmp_lem_pars[2] == tmp_lem_pars[3] == tmp_lem_pars[4] == '0') is True:
                # Get the saved default as market parameters
                lem_parameters = me.get_market_default_parameters()
            else:
                lem_parameters = {
                                     'pbBAU': tmp_lem_pars[1], 'psBAU': tmp_lem_pars[2],
                                     'pbP2P': tmp_lem_pars[3], 'psP2P': tmp_lem_pars[4], 'beta': tmp_lem_pars[5]
                                 }

            # Get the related measures
            lem_df = me.get_lem_df(ts_lem_start, players)

            # Solve the market
            players_balance = me.solve_single_lem(players_balance, lem_df, lem_parameters)

    # Finally move tokens
    logger.info('Balance: %s' % players_balance)
    me.apply_penalties_rewards(players_balance)

    logger.info('Ending program')

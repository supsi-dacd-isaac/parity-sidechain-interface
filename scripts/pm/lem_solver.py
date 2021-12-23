# Importing section
import datetime
import json
import argparse
import logging

from classes.market_engine import MarketEngine


def get_ts_end(ts, interval):
    if interval[-1] == 'm':
        factor = 60
    elif interval[-1] == 'h':
        factor = 60 * 60
    elif interval[-1] == 'd':
        factor = 60 * 60 * 24
    return ts - int(interval[0:-1])*factor


#  Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='configuration file')
    arg_parser.add_argument('-l', help='log file')

    args = arg_parser.parse_args()

    args = arg_parser.parse_args()
    cfg = json.loads(open(args.c).read())

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
    case = '1h'
    ts_end = int(datetime.datetime.now().replace(second=0).timestamp())
    ts_start = get_ts_end(ts_end, case)

    # Define the MarketEngine instance
    me = MarketEngine(cfg, logger)

    # Get the lem parameters, if None all the potential players will be considered in the LEM, which will have the default parameters
    lem_parameters, grid_state, players, aggregator = me.get_lem_features(ts_start, ts_end)

    if lem_parameters is None:
        # Load all the players and the default parameters
        players = me.get_all_players()
        lem_parameters = me.get_market_default_parameters()

    # print('PERIOD: [%i - %i]' % (ts_start, ts_end))
    # print('AGGREGATOR: %s' % aggregator)
    # print('GRID STATE: %s' % grid_state)
    # print('PLAYERS: %s' % players)
    # print('LEM PARAMETERS: %s' % lem_parameters)

    logger.info('Ending program')

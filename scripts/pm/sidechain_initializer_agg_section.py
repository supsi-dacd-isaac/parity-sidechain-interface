# Importing section
import json
import argparse
import logging
import time
import utilities as u

from classes.pseudonymizer import Pseudonymizer


def store_dataset(cmd, pars, logger):
    ret_data = u.send_post('%s/%s' % (url_prefix, cmd), pars, logger)
    time.sleep(8)
    u.send_get('%s/checkTx/%s' % (url_prefix, ret_data['tx_hash']), logger)


# Main
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='config file')
    arg_parser.add_argument('-l', help='log file')

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

    url_prefix = cfg['sidechainRestApi']
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    logger.info('Starting program')

    # Set the default market parameters
    for elem in cfg['defaultLemParameters']:
        params = {
            'lemCase': elem['gridState'],
            'pbBAU': elem['pbBAU'],
            'psBAU': elem['psBAU'],
            'pbP2P': elem['pbP2P'],
            'psP2P': elem['psP2P'],
            'beta': elem['beta'],
        }
        store_dataset('createDefaultLemPars', params, logger)

    logger.info('Ending program')

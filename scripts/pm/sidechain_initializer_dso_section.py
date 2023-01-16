# Importing section
import json
import argparse
import logging
import time
import utilities as u

from classes.pseudonymizer import Pseudonymizer


def store_dataset(cmd, pars, logger):
    u.send_post('%s/%s' % (url_prefix, cmd), pars, logger)
    time.sleep(8)


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

    pseudo = Pseudonymizer(cfg, logger)

    # Get the addresses
    accs_addrs = pseudo.get_addresses(cfg['accountsAddressesfile'])

    # Get the pseudonyms
    if cfg['pseudonymization']['enabled'] is True:
        pseudonyms = pseudo.get_pseudonyms()
    else:
        pseudonyms = None

    # Set the DSO
    idx = pseudo.get_identifier(pseudonyms, cfg['roles']['dso'])
    store_dataset('createDso', {'idx': idx, 'address': accs_addrs[idx]}, logger)

    # Set the Aggregator
    idx = pseudo.get_identifier(pseudonyms, cfg['roles']['aggregator'])
    store_dataset('createAggregator', {'idx': idx, 'address': accs_addrs[idx]}, logger)

    # Set the Market Operator
    idx = pseudo.get_identifier(pseudonyms, cfg['roles']['marketOperator'])
    store_dataset('createMarketOperator', {'idx': idx, 'address': accs_addrs[idx]}, logger)

    # Set the players
    for acc in cfg['roles']['prosumers']:
        idx = pseudo.get_identifier(pseudonyms, acc)
        store_dataset('createPlayer', {'idx': idx, 'address': accs_addrs[idx], 'role': 'prosumer'}, logger)

    logger.info('Ending program')

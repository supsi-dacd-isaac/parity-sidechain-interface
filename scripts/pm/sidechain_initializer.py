# Importing section
import json
import argparse
import logging
import time
import utilities as u


def get_addresses(input_file):
    fr = open(input_file, 'r')
    addrs = dict()
    for x in fr:
        if 'print_account_address' not in x:
            x = x[0:-1]
            (acc, addr) = x.split(',')
            addrs[acc] = addr
    fr.close()
    return addrs


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

    # Get the addresses
    accs_addrs = get_addresses(cfg['accountsAddressesfile'])

    # Set the DSO
    params = {'idx': cfg['roles']['dso'], 'address': accs_addrs[cfg['roles']['dso']]}
    store_dataset('createDso', params, logger)

    # Set the Aggregator
    params = {'idx': cfg['roles']['aggregator'], 'address': accs_addrs[cfg['roles']['aggregator']]}
    store_dataset('createAggregator', params, logger)

    # Set the Market Operator
    params = {'idx': cfg['roles']['marketOperator'], 'address': accs_addrs[cfg['roles']['marketOperator']]}
    store_dataset('createMarketOperator', params, logger)

    # Set the players
    for acc in cfg['roles']['prosumers']:
        params = {'idx': acc, 'address': accs_addrs[acc], 'role': 'prosumer'}
        store_dataset('createPlayer', params, logger)

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

# Importing section
import json
import argparse
import logging
import time
import requests
import http
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


def get_pseudonym(cfg, plain_text):
    res = requests.get(url='%s=%s' % (cfg['pseudonymization']['pseudonomizerWebService'], plain_text),
                       timeout=cfg['pseudonymization']['timeout'])

    if res.status_code == http.HTTPStatus.OK:
        return json.loads(res.text)['pseudonym']
    else:
        return None


def get_pseudonyms(cfg):
    pseudos = dict()
    for prosumer in cfg['roles']['prosumers']:
        pseudos[prosumer] = get_pseudonym(cfg, prosumer)

    return pseudos


def get_identifier(pseudos, idx):
    if pseudos is None:
        return idx
    else:
        return pseudos[idx]


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

    # Get the pseudonyms
    if cfg['pseudonymization']['enabled'] is True:
        pseudonyms = get_pseudonyms(cfg)
    else:
        pseudonyms = None

    # Set the DSO
    idx = get_identifier(pseudonyms, cfg['roles']['dso'])
    store_dataset('createDso', {'idx': idx, 'address': accs_addrs[idx]}, logger)

    # Set the Aggregator
    idx = get_identifier(pseudonyms, cfg['roles']['aggregator'])
    store_dataset('createAggregator', {'idx': idx, 'address': accs_addrs[idx]}, logger)

    # Set the Market Operator
    idx = get_identifier(pseudonyms, cfg['roles']['marketOperator'])
    store_dataset('createMarketOperator', {'idx': idx, 'address': accs_addrs[idx]}, logger)

    # Set the players
    for acc in cfg['roles']['prosumers']:
        idx = get_identifier(pseudonyms, acc)
        store_dataset('createPlayer', {'idx': idx, 'address': accs_addrs[idx], 'role': 'prosumer'}, logger)

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

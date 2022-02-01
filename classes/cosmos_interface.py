import http

import requests
import os
import json


class CosmosInterface:
    """
    CosmosInterface class for Cosmos SDK 0.39x
    """
    def __init__(self, cfg, logger):
        """
        Constructor
        :param cfg: configuration dictionary
        :type dict
        :param logger
        :type Logger
        """
        # define the main global variables
        self.cfg = cfg
        self.logger = logger
        self.full_path_app = '%s%sbin%s%sd' % (self.cfg['cosmos']['goRoot'], os.sep, os.sep, self.cfg['cosmos']['app'])
        self.url = 'http://%s:%i' % (self.cfg['server']['host'], self.cfg['server']['port'])
        self.local_account = self.get_account_info()

    def get_account_info(self):
        res = os.popen('%s keys list --output json' % self.full_path_app).read()
        accounts = json.loads(res)
        return accounts[0]

    def check_tx(self, tx_hash):
        if tx_hash is None or len(tx_hash) != 64:
            return http.HTTPStatus.NOT_FOUND, -1
        else:
            cmd = '%s query tx %s' % (self.full_path_app, tx_hash)

            try:
                res = os.popen(cmd).read()
                code = int(res.split('\n')[0].replace(' ', '').split(':')[1])
                return http.HTTPStatus.OK, code
            except Exception as e:
                self.logger.error('EXCEPTION: %s' % str(e))
                return http.HTTPStatus.INTERNAL_SERVER_ERROR, -1

    def do_query(self, end_point):
        url = '%s://%s:%i/%s%s' % (self.cfg['cosmos']['protocol'], self.cfg['cosmos']['host'],
                                   self.cfg['cosmos']['port'], self.cfg['cosmos']['requestEndpointHeader'], end_point)
        res = requests.get(url)
        return res.status_code, res.text

    def send_tokens(self, dest, amount):
        if amount > 0:
            self.do_token_transaction(dest, amount)
        else:
            self.logger.error('Amount to transfer must be > 0')

    def do_application_transaction(self, cmd, params):
        # Create the command header
        cmd_str = '%s tx %s' % (self.full_path_app, self.cfg['cosmos']['app'])

        # Customize the command if available
        real_cmd = self.customize_cmd(cmd, params)

        if real_cmd is not None:
            cmd_str = '%s %s' % (cmd_str, real_cmd)

            # Get the account
            account = self.get_account_info()

            # Add name of the local account performing the transaction
            cmd_str = '%s --from %s -y' % (cmd_str, account['name'])

            return self.perform_transaction_command(cmd_str)
        else:
            return http.HTTPStatus.NOT_FOUND, None, 'Command %s not available' % cmd

    def do_token_transaction(self, dest, amount):
        cmd_str = '%s tx bank send %s %s %i%s -y' % (self.full_path_app, self.local_account['address'],
                                                     dest['address'], amount, self.cfg['cosmos']['tokenName'])

        return self.perform_transaction_command(cmd_str)

    def perform_transaction_command(self, cmd_str):
        self.logger.info('Transaction command: %s' % cmd_str)
        try:
            res = os.popen(cmd_str).read()
            tx = res.split('\n')[-2].split(': ')[1]

            # check the transaction length
            if len(tx) == 64:
                return http.HTTPStatus.OK, tx, ''
            else:
                return http.HTTPStatus.INTERNAL_SERVER_ERROR, tx, 'txHash length != 64'
        except Exception as e:
            self.logger.error('EXCEPTION: %s' % str(e))
            return http.HTTPStatus.INTERNAL_SERVER_ERROR, None, 'Transaction performing not successful'

    def handle_get(self, endpoint, key=None):
        endpoint = '%s%s' % (self.url, endpoint)
        if key is None:
            key = endpoint.split('/')[3]

        res = requests.get(endpoint)

        if res.status_code == http.HTTPStatus.OK:
            data = json.loads(res.text)
            return data[key]
        else:
            self.logger.warning('Endpoint %s has responded with code %i, None returned' % (endpoint, res.status_code))
            return None



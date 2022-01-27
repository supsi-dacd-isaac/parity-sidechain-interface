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

    def send_tokens(self, src, dest, amount):
        if amount > 0:
            cmd_str = '%s tx bank send %s %s %i%s -y' % (self.full_path_app, src['address'], dest['address'], amount,
                                                         self.cfg['cosmos']['tokenName'])
            self.logger.warning('NOT ACTUATED TRANSACTION: %s' % cmd_str)
            # self.perform_transaction_command(cmd_str)
        else:
            self.logger.error('Amount to transfer must be > 0')

    def do_transaction(self, cmd, params):
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

    # @staticmethod
    # def customize_cmd(endpoint, params):
    #     if endpoint == '/createDso':
    #         return 'create-dso %s %s' % (params['idx'], params['address'])
    #
    #     elif endpoint == '/updateDso':
    #         return 'update-dso %s %s' % (params['idx'], params['address'])
    #
    #     elif endpoint == '/createAggregator':
    #         return 'create-aggregator %s %s' % (params['idx'], params['address'])
    #
    #     elif endpoint == '/updateAggregator':
    #         return 'update-aggregator %s %s' % (params['idx'], params['address'])
    #
    #     elif endpoint == '/createMarketOperator':
    #         return 'create-market-operator %s %s' % (params['idx'], params['address'])
    #
    #     elif endpoint == '/updateMarketOperator':
    #         return 'update-market-operator %s %s' % (params['idx'], params['address'])
    #
    #     elif endpoint == '/createPlayer':
    #         return 'create-player %s %s %s %s' % (params['idx'], params['idx'], params['address'], params['role'])
    #
    #     elif endpoint == '/updatePlayer':
    #         return 'update-player %s %s %s %s' % (params['idx'], params['idx'], params['address'], params['role'])
    #
    #     elif endpoint == '/createDefaultLemPars':
    #         return 'create-default-lem-pars %s %s %s %s %s %s' % (params['lemCase'], params['pbBAU'], params['psBAU'],
    #                                                               params['pbP2P'], params['psP2P'], params['beta'])
    #
    #     elif endpoint == '/createGridState':
    #         return 'create-grid-state %s-%s %s %s %s' % (params['timestamp'], params['grid'], params['grid'],
    #                                                      params['timestamp'], params['state'])
    #
    #     elif endpoint == '/createLem':
    #         result = 'create-lem %s-%s-%s %s %s %s' % (params['start'], params['end'], params['aggregator'],
    #                                                    params['start'], params['end'], params['case'])
    #         for mp in params['marketParameters']:
    #             result = '%s %s' % (result, mp)
    #
    #         for p in params['players']:
    #             result = '%s %s' % (result, p)
    #         return result
    #
    #     elif endpoint == '/createLemMeasure':
    #         return 'create-lem-measure %s-%s-%s %s %s %s %s %s' % (params['player'], params['signal'],
    #                                                                params['timestamp'], params['player'],
    #                                                                params['signal'], params['timestamp'],
    #                                                                str(params['value']), params['measureUnit'])
    #     elif endpoint == '/createLemDataset':
    #         return 'create-lem-dataset %s-%s %s %s %s %s %s %s' % (params['player'],
    #                                                                params['timestamp'],
    #                                                                params['player'],
    #                                                                params['timestamp'],
    #                                                                str(params['powerConsumptionMeasure']),
    #                                                                str(params['powerProductionMeasure']),
    #                                                                str(params['powerConsumptionForecast']),
    #                                                                str(params['powerProductionForecast']))
    #
    #     elif endpoint == '/createSla':
    #         return 'create-sla %s %s %s' % (params['idx'], params['start'], params['end'])
    #
    #     elif endpoint == '/updateSla':
    #         return 'update-sla %s %s %s' % (params['idx'], params['start'], params['end'])
    #
    #     elif endpoint == '/createKpi':
    #         return 'create-kpi %s %s %s %s %s %s' % (params['idx'], params['idxSla'], params['rule'],
    #                                                  str(params['limit']), params['measureUnit'], params['penalty'])
    #
    #     elif endpoint == '/updateKpi':
    #         return 'update-kpi %s %s %s %s %s %s' % (params['idx'], params['idxSla'], params['rule'],
    #                                                  str(params['limit']), params['measureUnit'], params['penalty'])
    #
    #     elif endpoint == '/createKpiMeasure':
    #         return 'create-kpi-measure %s-%s-%s %s %s %s %s %s' % (params['player'], params['kpi'],
    #                                                                params['timestamp'], params['kpi'],
    #                                                                params['player'], params['timestamp'],
    #                                                                str(params['value']), params['measureUnit'])
    #
    #     else:
    #         return None
    #
    # def handle_get(self, endpoint, key=None):
    #     endpoint = '%s%s' % (self.url, endpoint)
    #     if key is None:
    #         key = endpoint.split('/')[3]
    #
    #     res = requests.get(endpoint)
    #
    #     if res.status_code == http.HTTPStatus.OK:
    #         data = json.loads(res.text)
    #         return data[key]
    #     else:
    #         self.logger.warning('Endpoint %s has responded with code %i, None returned' % (endpoint, res.status_code))
    #         return None
    #
    # def get_all_players(self):
    #     return self.handle_get('/player')
    #
    # def get_aggregator(self):
    #     return self.handle_get('/aggregator', 'Aggregator')
    #
    # def get_dso(self):
    #     return self.handle_get('/dso', 'Dso')



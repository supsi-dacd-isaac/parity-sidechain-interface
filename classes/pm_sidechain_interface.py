import http

import requests
import os
import json

from classes.cosmos_interface import CosmosInterface


class PMSidechainInterface(CosmosInterface):
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
        super().__init__(cfg, logger)
        self.local_account = None
        self.aggregator = None
        self.dso = None

    def set_main_sidechain_nodes_info(self):
        self.local_account = self.get_account_info()
        self.aggregator = self.get_aggregator()
        self.dso = self.get_dso()

    @staticmethod
    def customize_cmd(endpoint, params):
        if endpoint == '/createDso':
            return 'create-dso %s %s' % (params['idx'], params['address'])

        elif endpoint == '/updateDso':
            return 'update-dso %s %s' % (params['idx'], params['address'])

        elif endpoint == '/createAggregator':
            return 'create-aggregator %s %s' % (params['idx'], params['address'])

        elif endpoint == '/updateAggregator':
            return 'update-aggregator %s %s' % (params['idx'], params['address'])

        elif endpoint == '/createMarketOperator':
            return 'create-market-operator %s %s' % (params['idx'], params['address'])

        elif endpoint == '/updateMarketOperator':
            return 'update-market-operator %s %s' % (params['idx'], params['address'])

        elif endpoint == '/createPlayer':
            return 'create-player %s %s %s %s' % (params['idx'], params['idx'], params['address'], params['role'])

        elif endpoint == '/updatePlayer':
            return 'update-player %s %s %s %s' % (params['idx'], params['idx'], params['address'], params['role'])

        elif endpoint == '/createDefaultLemPars':
            return 'create-default-lem-pars %s %s %s %s %s %s' % (params['lemCase'], params['pbBAU'], params['psBAU'],
                                                                  params['pbP2P'], params['psP2P'], params['beta'])

        elif endpoint == '/createGridState':
            return 'create-grid-state %s-%s %s %s %s' % (params['timestamp'], params['grid'], params['grid'],
                                                         params['timestamp'], params['state'])

        elif endpoint == '/createLem':
            result = 'create-lem %s-%s-%s %s %s %s' % (params['start'], params['end'], params['aggregator'],
                                                       params['start'], params['end'], params['case'])
            for mp in params['marketParameters']:
                result = '%s %s' % (result, mp)

            for p in params['players']:
                result = '%s %s' % (result, p)
            return result

        elif endpoint == '/createKpiFeatures':
            result = 'create-kpi-features %s %s %s %s %s %s' % (params['idx'], params['idxSla'], params['rule'],
                                                                str(params['limit']), params['measureUnit'],
                                                                params['penalty'])

            for p in params['players']:
                result = '%s %s' % (result, p)
            return result

        elif endpoint == '/createLemMeasure':
            return 'create-lem-measure %s-%s-%s %s %s %s %s %s' % (params['player'], params['signal'],
                                                                   params['timestamp'], params['player'],
                                                                   params['signal'], params['timestamp'],
                                                                   str(params['value']), params['measureUnit'])
        elif endpoint == '/createLemDataset':
            return 'create-lem-dataset %s-%s %s %s %s %s %s %s' % (params['player'],
                                                                   params['timestamp'],
                                                                   params['player'],
                                                                   params['timestamp'],
                                                                   str(params['powerConsumptionMeasure']),
                                                                   str(params['powerProductionMeasure']),
                                                                   str(params['powerConsumptionForecast']),
                                                                   str(params['powerProductionForecast']))

        elif endpoint == '/createSla':
            return 'create-sla %s %s %s' % (params['idx'], params['start'], params['end'])

        elif endpoint == '/updateSla':
            return 'update-sla %s %s %s' % (params['idx'], params['start'], params['end'])

        elif endpoint == '/createKpi':
            return 'create-kpi %s %s %s %s %s %s' % (params['idx'], params['idxSla'], params['rule'],
                                                     str(params['limit']), params['measureUnit'], params['penalty'])

        elif endpoint == '/updateKpi':
            return 'update-kpi %s %s %s %s %s %s' % (params['idx'], params['idxSla'], params['rule'],
                                                     str(params['limit']), params['measureUnit'], params['penalty'])

        elif endpoint == '/createKpiMeasure':
            return 'create-kpi-measure %s-%s-%s %s %s %s %s %s' % (params['player'], params['kpi'],
                                                                   params['timestamp'], params['kpi'],
                                                                   params['player'], params['timestamp'],
                                                                   str(params['value']), params['measureUnit'])

        else:
            return None

    def get_all_players(self):
        return self.handle_get('/player')

    def get_aggregator(self):
        return self.handle_get('/aggregator', 'Aggregator')

    def get_dso(self):
        return self.handle_get('/dso', 'Dso')

    def get_all_available_prosumers(self):
        res = requests.get('%s/player' % self.url)
        if res.status_code == http.HTTPStatus.OK:
            players = json.loads(res.text)['player']
            players_idxs = []
            for player in players:
                if player['role'] == 'prosumer':
                    players_idxs.append(player['idx'])
        else:
            self.logger.warning('No prosumers are available')
            players_idxs = None
        return players_idxs

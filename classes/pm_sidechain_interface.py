import http
import requests
import json
import numpy as np
from datetime import timedelta

from classes.cosmos_interface import CosmosInterface
from classes.time_utils import TimeUtils
from classes.pseudonymizer import Pseudonymizer


class PMSidechainInterface(CosmosInterface):
    """
    CosmosInterface class for Cosmos SDK 0.39x
    """
    def __init__(self, cfg, logger, server_pm_flag):
        """
        Constructor
        :param cfg: configuration dictionary
        :type dict
        :param logger
        :type Logger
        """
        super().__init__(cfg, logger, server_pm_flag)
        self.aggregator = None
        self.dso = None
        self.pseudonymizer = Pseudonymizer(cfg, logger)

        self.GRIDSTATE_RED = 'RED'
        self.GRIDSTATE_YELLOW = 'YELLOW'
        self.GRIDSTATE_GREEN = 'GREEN'

        self.default_grid_state = self.GRIDSTATE_GREEN
        self.grid_state = None

    def set_main_sidechain_nodes_info(self):
        self.aggregator = self.get_aggregator()
        self.dso = self.get_dso()

    def do_application_transaction(self, cmd, params):
        # Create the command header
        cmd_str = '%s tx %s' % (self.full_path_app, self.cfg['cosmos']['app'])

        # Customize the command if available
        if self.cfg['cosmos']['app'] == 'pm':
            real_cmd = self.pm_cmd_customization(cmd, params)

            if real_cmd is not None:
                cmd_str = '%s %s' % (cmd_str, real_cmd)

                # Add name of the local account performing the transaction
                cmd_str = '%s --from %s -y' % (cmd_str, self.local_account['name'])

                return self.perform_transaction_command(cmd_str)
            else:
                return http.HTTPStatus.NOT_FOUND, None, \
                       'Command %s not available for node %s, address %s' % (cmd, self.local_account['name'],
                                                                             self.local_account['address'])
        else:
            return http.HTTPStatus.NOT_FOUND, None, 'Command not available for application %s' % self.cfg['cosmos']['app']

    def pm_cmd_customization(self, endpoint, params):
        if endpoint == '/createDso':
            return 'create-dso %s %s' % (self.get_idx(params['idx']), params['address'])

        elif endpoint == '/createAggregator':
            return 'create-aggregator %s %s' % (self.get_idx(params['idx']), params['address'])

        elif endpoint == '/createMarketOperator':
            return 'create-market-operator %s %s' % (self.get_idx(params['idx']), params['address'])

        elif endpoint == '/createPlayer':
            return 'create-player %s %s %s %s' % (self.get_idx(params['idx']), params['idx'], params['address'],
                                                  params['role'])

        elif endpoint == '/createDefaultLemPars':
            return 'create-default-lem-pars %s %s %s %s %s %s' % (params['lemCase'], params['pbBAU'], params['psBAU'],
                                                                  params['pbP2P'], params['psP2P'], params['beta'])

        elif endpoint == '/createGridState':
            return 'create-grid-state %s-%s %s %s %s' % (params['timestamp'], params['grid'], params['grid'],
                                                         params['timestamp'], params['state'])

        elif endpoint == '/createLem':
            result = 'create-lem %s-%s-%s %s %s %s' % (params['start'], params['end'], params['aggregator'],
                                                       params['start'], params['end'], params['state'])
            for mp in params['marketParameters']:
                result = '%s %s' % (result, mp)

            # Insert a player in the LEM only tit has enough tokens in the balance
            for p in self.check_players_availability(params['players'], self.cfg['balanceController']['minimumAmount']):
                result = '%s %s' % (result, p)
            return result

        elif endpoint == '/updateLem':
            idx = '%i-%i-%s' % (params['start'], params['end'], params['aggregator'])
            data = self.do_query('/lem/%s' % idx)
            lem_data = json.loads(data[1])
            result = 'update-lem %s %s %s' % (idx, params['start'], params['end'])

            # Set the new state
            result = '%s %s' % (result, params['state'])

            # Set the other LEM parameters
            for mp in lem_data['lem']['params'][1:]:
                result = '%s %s' % (result, mp)

            # Insert in the LEM only the player with enough tokens in the balance
            for p in lem_data['lem']['players']:
                result = '%s %s' % (result, p)

            return result

        elif endpoint == '/createLemMeasure':
            return 'create-lem-measure %s-%s-%s %s %s %s %s %s' % (params['player'], params['signal'],
                                                                   params['timestamp'], params['player'],
                                                                   params['signal'], params['timestamp'],
                                                                   str(params['value']), params['measureUnit'])


        elif endpoint == '/createForecast':
            if len(params['values']) <= 96:
                result = 'create-forecast %s %s' % (self.local_account['name'], params['ts'])
                for val in params['values']:
                    result = '%s %s' % (result, val)
                return result
            else:
                return None

        elif endpoint == '/updateForecast':
            if len(params['values']) <= 96:
                result = 'update-forecast %s %s' % (self.local_account['name'], params['ts'])
                for val in params['values']:
                    result = '%s %s' % (result, val)
                return result
            else:
                return None

        elif endpoint == '/createLemDataset':
            # Get balance
            bal_st, bal_data = self.do_query('/balances/%s' % self.local_account['address'])
            if int(json.loads(bal_data)['balances'][0]['amount']) >= self.cfg['balanceController']['minimumAmount']:
                return 'create-lem-dataset %s-%s %s %s %s %s %s %s' % (params['player'],
                                                                       params['timestamp'],
                                                                       params['player'],
                                                                       params['timestamp'],
                                                                       str(params['powerConsumptionMeasure']),
                                                                       str(params['powerProductionMeasure']),
                                                                       str(params['powerConsumptionForecast']),
                                                                       str(params['powerProductionForecast']))
            else:
                return None

        elif endpoint == '/createSla':
            return 'create-sla %s %s %s' % (params['idx'], params['start'], params['end'])

        elif endpoint == '/createKpiFeatures':
            result = 'create-kpi-features %s %s %s %s %s %s' % (params['idx'], params['idxSla'], params['rule'],
                                                                str(params['limit']), params['measureUnit'],
                                                                params['penalty'])

            for p in params['players']:
                result = '%s %s' % (result, self.get_idx(p))
            return result

        elif endpoint == '/createKpiMeasure':
            return 'create-kpi-measure %s-%s-%s %s %s %s %s %s' % (params['player'], params['kpi'],
                                                                   params['timestamp'], params['kpi'],
                                                                   params['player'], params['timestamp'],
                                                                   str(params['value']), params['measureUnit'])

        else:
            return None

    def get_all_players(self):
        return self.handle_get('/player')

    def get_single_player(self, idx):
        return self.handle_get('/player/%s' % idx)

    def get_aggregator(self):
        return self.handle_get('/aggregator', 'Aggregator')

    def get_dso(self):
        return self.handle_get('/dso', 'Dso')

    def get_balance(self, addr):
        return self.handle_get('/balances/%s' % addr, None)

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

    def get_idx(self, candidate):
        if self.cfg['pseudonymization']['enabled'] is True:
            return self.pseudonymizer.get_pseudonym(candidate)
        else:
            return candidate

    def check_players_availability(self, candidates, min_amount):
        winners = list()
        for candidate in candidates:
            idx_candidate = self.get_idx(candidate)

            req_status, req_data = self.do_query('/player')
            data = json.loads(req_data)
            for player in data['player']:
                if idx_candidate == player['idx']:
                    # Get balance
                    bal_st, bal_data = self.do_query('/balances/%s' % player['address'])
                    if int(json.loads(bal_data)['balances'][0]['amount']) >= min_amount:
                        winners.append(idx_candidate)

        return winners

    def get_lem_features(self, ts_start, ts_end):
        aggregator = self.get_aggregator()
        lem_info = self.handle_get('/lem/%i-%i-%s' % (ts_start, ts_end, aggregator['idx']))
        return lem_info['players'], aggregator, lem_info['params']

    def get_market_default_parameters(self):
        if self.grid_state is not None:
            return self.handle_get('/defaultLemPars/%s' % self.grid_state)
        else:
            return self.handle_get('/defaultLemPars/%s' % self.default_grid_state)

    def get_forecast(self, node):
        return self.handle_get('/forecast/%s' % node)

    def get_grid_state(self, ts):
        grid_state = self.handle_get('/gridState/%i-%s' % (ts, self.cfg['grid']['name']))
        if grid_state is not None:
            self.grid_state = grid_state['state']
            return self.grid_state
        else:
            self.grid_state = None
            return self.default_grid_state

    @staticmethod
    def calc_lem_energy_prices(ec_tot, ep_tot, lem_parameters):
        # EXAMPLE: LAUNCHED @12:05, LAST SAVED LEM -> [12:00-12:15]
        #
        # IF PARS OF LEM [12:00-12:15] ARE CUSTOMIZED
        #       IF STATE OF LEM [12:00-12:15] IS GREEN
        #               USE THE CUSTOMIZED PARS
        #       ELSE
        #               USE THE DEFAULT PARS (GREEN CASE)
        # ELSE
        #       USE THE DEFAULT PARS (GREEN CASE)

        # Transform prices from cts (string) to CHF (float)
        pb_bau = float(lem_parameters['pbBAU']) / 100
        pb_p2p = float(lem_parameters['pbP2P']) / 100
        ps_bau = float(lem_parameters['psBAU']) / 100
        ps_p2p = float(lem_parameters['psP2P']) / 100

        if ec_tot > 0:
            p_buy = (ec_tot * pb_bau - np.min([ec_tot, ep_tot])*(pb_bau-pb_p2p)) / ec_tot
        else:
            p_buy = pb_bau

        if ep_tot > 0:
            p_sell = (ep_tot * ps_bau - np.min([ec_tot, ep_tot])*(ps_bau-ps_p2p)) / ep_tot
        else:
            p_sell = ps_bau
        return p_buy, p_sell

    def calc_forecast_energy_prices(self):
        dt_lem_start = TimeUtils.get_dt(time_zone=self.cfg['utils']['timeZone'], str_dt='now_s00', flag_set_minute=False)
        dt_lem_start = dt_lem_start - timedelta(minutes=self.cfg['shiftBackMinutes']['energyPriceDownload'])
        dt_lem_end = TimeUtils.get_end_dt(dt_lem_start, self.cfg['lem']['duration'])
        _, aggregator, lem_pars = self.get_lem_features(int(dt_lem_start.timestamp()), int(dt_lem_end.timestamp()))

        # Check if the last parameters are customized
        if lem_pars[1] == '0' and lem_pars[2] == '0' and lem_pars[3] == '0' and lem_pars[4] == '0':
            pars = self.get_market_default_parameters()
        else:
            if self.get_grid_state(int(dt_lem_start.timestamp())) == self.GRIDSTATE_GREEN:
                pars = {
                           'pbBAU': float(lem_pars[1]), 'psBAU': float(lem_pars[2]),
                           'pbP2P': float(lem_pars[3]), 'psP2P': float(lem_pars[4])
                       }
            else:
                pars = self.get_market_default_parameters()

        # Get the players
        players = self.get_all_players()

        # Get aggregator forecasts
        forecasts_aggregator = self.get_forecast(aggregator['idx'])
        forecasts_players = {}
        for player in players:
            forecasts_players[player['idx']] = self.get_forecast(player['idx'])

        # Calculate the total energies (cons + prod) matrices
        ec_tot = np.zeros(len(forecasts_aggregator['values']))
        ep_tot = np.zeros(len(forecasts_aggregator['values']))
        for i in range(0, len(ec_tot)):
            # Initialize with the aggregator forecasts
            (ec, ep) = forecasts_aggregator['values'][i].split(',')
            ec_tot[i] = float(ec)
            ep_tot[i] = float(ep)

            # Cycle over the players
            for k_player in forecasts_players.keys():
                (ec, ep) = forecasts_players[k_player]['values'][i].split(',')
                ec_tot[i] += float(ec)
                ep_tot[i] += float(ep)

        # Calculate the prices matrices
        prices_buy = np.zeros(len(forecasts_aggregator['values']))
        prices_sell = np.zeros(len(forecasts_aggregator['values']))
        for i in range(0, len(ec_tot)):
            prices_buy[i], prices_sell[i] = PMSidechainInterface.calc_lem_energy_prices(ec_tot[i], ep_tot[i], pars)

        # Return the data
        return {
                    'lemStartingTimestamp': int(dt_lem_start.timestamp()),
                    'aggregatorForecasts': forecasts_aggregator,
                    'playersForecasts': forecasts_players,
                    'buyingPrices': list(prices_buy),
                    'sellingPrices': list(prices_sell)
               }

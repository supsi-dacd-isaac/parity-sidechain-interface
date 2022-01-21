import http
import requests
import numpy as np
import pandas as pd
import json

from classes.cosmos_interface import CosmosInterface


class MarketEngine:
    """
    MarketEngine class
    """
    def __init__(self, cfg, logger):
        """
        Constructor
        :param cfg: configuration dictionary
        :type dict
        :param logger
        :type Logger
        """
        self.cfg = cfg
        self.logger = logger
        self.url = 'http://%s:%i' % (self.cfg['server']['host'], self.cfg['server']['port'])
        self.default_grid_state = 'GREEN'
        self.grid_state = None
        self.ci = CosmosInterface(cfg, logger)

    def handle_get(self, endpoint, key=None):
        if key is None:
            key = endpoint.split('/')[3]

        res = requests.get(endpoint)

        if res.status_code == http.HTTPStatus.OK:
            data = json.loads(res.text)
            return data[key]
        else:
            self.logger.warning('Endpoint %s has responded with code %i, None returned' % (endpoint, res.status_code))
            return None

    def get_lem_features(self, ts_start, ts_end):
        # Still to be implemented for the players
        aggregator = self.get_aggregator()
        lem_info = self.handle_get('%s/lem/%i-%i-%s' % (self.url, ts_start, ts_end, aggregator['idx']))
        return lem_info['players'], aggregator

    def get_grid_state(self, ts):
        grid_state = self.handle_get('%s/gridState/%i-%s' % (self.url, ts, self.cfg['grid']['name']))
        if grid_state is not None:
            self.grid_state = list(grid_state.values())[3]
            return self.grid_state
        else:
            self.grid_state = None
            return self.default_grid_state

    def get_all_players(self):
        return self.handle_get('%s/player' % self.url)

    def get_aggregator(self):
        return self.handle_get('%s/aggregator' % self.url, 'Aggregator')

    def get_dso(self):
        return self.handle_get('%s/dso' % self.url, 'Dso')

    def get_market_default_parameters(self):
        if self.grid_state is not None:
            return self.handle_get('%s/defaultLemPars/%s' % (self.url, self.grid_state))
        else:
            return self.handle_get('%s/defaultLemPars/%s' % (self.url, self.default_grid_state))

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

    def get_lem_df(self, ts, players):
        lem_raw_data = []
        for player in players:
            data = self.handle_get('%s/lemDataset/%s-%i' % (self.url, player, ts))
            if data is not None:
                lem_raw_data.append({'player': data['player'],
                                     'ec': self.power_to_energy(float(data['pconsMeasure']),
                                                                int(self.cfg['lem']['marketsDuration'][0:-1]),
                                                                self.cfg['lem']['marketsDuration'][-1],
                                                                self.cfg['lem']['powerToKW']),
                                     'ep': self.power_to_energy(float(data['pprodMeasure']),
                                                                int(self.cfg['lem']['marketsDuration'][0:-1]),
                                                                self.cfg['lem']['marketsDuration'][-1],
                                                                self.cfg['lem']['powerToKW'])
                                     })

        df = pd.DataFrame(lem_raw_data, columns=['player', 'ec', 'ep'])
        return df.set_index('player')

    def solve_single_lem(self, players_balance, lem_df, lem_parameters):

        ec_tot = lem_df['ec'].sum()
        ep_tot = lem_df['ep'].sum()
        # ef_tot = ec_tot - ep_tot

        # Transform prices from cts (string) to CHF (float)
        pb_bau = float(lem_parameters['pbBAU']) / 100
        pb_p2p = float(lem_parameters['pbP2P']) / 100
        ps_bau = float(lem_parameters['psBAU']) / 100
        ps_p2p = float(lem_parameters['psP2P']) / 100
        # beta = float(lem_parameters['psP2P'])

        if ec_tot > 0:
            p_buy = (ec_tot * pb_bau - np.min([ec_tot, ep_tot])*(pb_bau-pb_p2p)) / ec_tot
        else:
            p_buy = pb_bau

        if ep_tot > 0:
            p_sell = (ep_tot * ps_bau - np.min([ec_tot, ep_tot])*(ps_bau-ps_p2p)) / ep_tot
        else:
            p_sell = ps_bau

        for player in lem_df.index:
            tkns_cons = int(round(lem_df['ec'][player] * p_buy * self.cfg['lem']['currency2Tkn'], 0))
            tkns_prod = int(round(lem_df['ep'][player] * p_sell * self.cfg['lem']['currency2Tkn'], 0))
            # todo beta (ef -> energy flow) still to be implemented
            players_balance[player] += tkns_prod - tkns_cons

        return players_balance

    @staticmethod
    def power_to_energy(power, res, case, scale):
        if case == 'm':
            return power * res * scale / 60
        elif case == 'h':
            return power * res * scale
        elif case == 'd':
            return power * res * scale * 24

    def move_tokens(self, balances):
        account = self.ci.get_account_info()
        dso = self.get_dso()

        # Check if the node is the DSO -> if yes rewards handling, else penalty handling
        if dso['idx'] == account['name']:
            self.rewards_handling(balances, dso, account)
        else:
            self.penalty_handling(balances, dso, account)
        # self.penalty_handling(balances, dso, account)

    def penalty_handling(self, balances, dso, account):
        if balances[account['name']] < 0:
            amount = abs(balances[account['name']])
            self.logger.info('PENALTY: Transfer %i tokens from %s to %s' % (amount,
                                                                            account['address'], dso['address']))
            self.ci.send_tokens(account, dso, amount)

    def rewards_handling(self, balances, dso, account):
        for k_node in balances:
            if balances[k_node] > 0:
                # Cycle over the players to see if there are production
                self.logger.info('REWARD: Transfer %i tokens from %s to %s' % (balances[k_node], dso['address'],
                                                                               account['address']))
                self.ci.send_tokens(dso, account, balances[k_node])





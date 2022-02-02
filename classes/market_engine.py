import numpy as np
import pandas as pd

from classes.pm_sidechain_interface import PMSidechainInterface


class MarketEngine(PMSidechainInterface):
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
        super().__init__(cfg, logger)

        self.default_grid_state = 'GREEN'
        self.grid_state = None

    def get_lem_features(self, ts_start, ts_end):
        aggregator = self.get_aggregator()
        lem_info = self.handle_get('/lem/%i-%i-%s' % (ts_start, ts_end, aggregator['idx']))
        return lem_info['players'], aggregator

    def get_market_default_parameters(self):
        if self.grid_state is not None:
            return self.handle_get('/defaultLemPars/%s' % self.grid_state)
        else:
            return self.handle_get('/defaultLemPars/%s' % self.default_grid_state)

    def get_grid_state(self, ts):
        grid_state = self.handle_get('/gridState/%i-%s' % (ts, self.cfg['grid']['name']))
        if grid_state is not None:
            self.grid_state = grid_state['state']
            return self.grid_state
        else:
            self.grid_state = None
            return self.default_grid_state

    def get_lem_df(self, ts, players):
        lem_raw_data = []
        for player in players:
            data = self.handle_get('/lemDataset/%s-%i' % (player, ts))
            self.logger.info('Downloaded data %s' % data)
            if data is not None:
                lem_raw_data.append({'player': data['player'],
                                     'ec': self.power_to_energy(float(data['pconsMeasure']),
                                                                int(self.cfg['lem']['duration'][0:-1]),
                                                                self.cfg['lem']['duration'][-1],
                                                                self.cfg['lem']['powerToKW']),
                                     'ep': self.power_to_energy(float(data['pprodMeasure']),
                                                                int(self.cfg['lem']['duration'][0:-1]),
                                                                self.cfg['lem']['duration'][-1],
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

    def apply_penalties_rewards(self, balances):
        # Check if the node is the DSO -> if yes rewards handling, else penalty handling
        if self.dso['idx'] == self.local_account['name']:
            # Producers management, run by DSO
            self.rewards_handling(balances)
        else:
            # Consumer management, run by player itself
            self.penalty_handling(balances)

    def penalty_handling(self, balances):
        if balances[self.local_account['name']] < 0:
            amount = abs(balances[self.local_account['name']])
            self.logger.info('PENALTY: Transfer %i tokens from %s to %s' % (amount, self.local_account['address'],
                                                                            self.dso['address']))
            self.send_tokens(self.dso, amount)

    def rewards_handling(self, balances):
        # Cycle over the players to see if there are producers
        for k_node in balances:
            if balances[k_node] > 0:
                # Get destination address
                dest = self.get_single_player(k_node)
                self.logger.info('REWARD: Transfer %i tokens from %s to %s' % (balances[k_node], self.dso['address'],
                                                                               dest['address']))
                self.send_tokens(dest, balances[k_node])

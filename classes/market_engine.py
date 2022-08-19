import time
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
        super().__init__(cfg, logger, False)

    def get_lem_df(self, ts, players):
        lem_raw_data = []
        if len(players) > 0:
            for player in players:
                endpoint = '/lemDataset/%s-%i' % (player, ts)
                self.logger.info('GET: %s' % endpoint)
                data = self.handle_get(endpoint)
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
                else:
                    self.logger.warning('No data available on endpoint %s' % endpoint)
        else:
            self.logger.warning('No players available for this LEM')

        df = pd.DataFrame(lem_raw_data, columns=['player', 'ec', 'ep'])
        return df.set_index('player')

    def solve_single_lem(self, players_balance, lem_df, lem_parameters):

        ec_tot = lem_df['ec'].sum()
        ep_tot = lem_df['ep'].sum()
        ef_tot = ec_tot - ep_tot

        # Calculate the energy prices
        p_buy, p_sell = PMSidechainInterface.calc_lem_energy_prices(ec_tot, ep_tot, lem_parameters)

        for player in lem_df.index:
            # 1) Token penalty related to energy consumption
            tkns_cons = int(round(lem_df['ec'][player] * p_buy * self.cfg['lem']['currency2Tkn'], 0))

            # 2) Token penalty related to energy production
            tkns_prod = int(round(lem_df['ep'][player] * p_sell * self.cfg['lem']['currency2Tkn'], 0))

            # 3) Token penalty related to energy flow
            ef_node = lem_df['ec'][player] - lem_df['ep'][player]
            # - ef_node * ef_tot > 0 => the node has followed the community => quadratic penalty
            # - ef_node * ef_tot < 0 => the node has not followed the community => quadratic reward
            tkns_flow = int(float(lem_parameters['beta']) * ef_node * ef_tot * self.cfg['lem']['currency2Tkn'])

            # 4) New player balance (N.B. tkns_flow is negative in case of reward)
            players_balance[player] += tkns_prod - tkns_cons - tkns_flow

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
        # Check if the node is the aggregator -> if yes rewards handling, else penalty handling
        if self.aggregator['idx'] == self.local_account['name']:
            # Producers management, run by aggregator
            self.rewards_handling(balances)
        else:
            # Consumer management, run by player itself
            self.penalty_handling(balances)

    def penalty_handling(self, balances):
        if balances[self.local_account['name']] < 0:
            amount = abs(balances[self.local_account['name']])
            self.logger.info('PENALTY: Transfer %i tokens from %s to %s' % (amount, self.local_account['address'],
                                                                            self.aggregator['address']))
            self.send_tokens(self.aggregator, amount)

    def rewards_handling(self, balances):
        # Cycle over the players to see if there are producers
        for k_node in balances:
            if balances[k_node] > 0:
                # Get destination address
                dest = self.get_single_player(k_node)
                self.logger.info('REWARD: Transfer %i tokens from %s to %s' % (balances[k_node],
                                                                               self.aggregator['address'],
                                                                               dest['address']))
                self.send_tokens(dest, balances[k_node])
                time.sleep(self.cfg['utils']['sleepBetweenTransactions'])

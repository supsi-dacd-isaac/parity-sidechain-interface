import http
import requests
import enum
import json


class GridStates(enum.Enum):
    Red = 'RED'
    Yellow = 'YELLOW'
    Green = 'GREEN'


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
        self.default_grid_state = GridStates.Green
        self.grid_state = None

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
        # Still to be implemented
        # lem_info = self.handle_get('%s/lem/xxxxx' % self.url)
        return None, self.get_grid_state(ts_start), None, self.get_aggregator()

    def get_grid_state(self, ts):
        grid_state = self.handle_get('%s/gridState/%i' % (self.url, ts))
        if grid_state is not None:
            self.grid_state = grid_state
            return grid_state
        else:
            self.grid_state = None
            return self.default_grid_state

    def get_all_players(self):
        return self.handle_get('%s/player' % self.url)

    def get_aggregator(self):
        return self.handle_get('%s/aggregator' % self.url, 'Aggregator')

    def get_market_default_parameters(self):
        if self.grid_state is not None:
            return self.handle_get('%s/defaultLemPars/%s' % (self.url, self.grid_state.value))
        else:
            return self.handle_get('%s/defaultLemPars/%s' % (self.url, self.default_grid_state.value))




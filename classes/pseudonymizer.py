import http

import requests
import os
import json


class Pseudonymizer:
    """
    Pseudonymizer class
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

    def get_addresses(self, input_file):
        fr = open(input_file, 'r')
        addrs = dict()
        for x in fr:
            if 'print_account_address' not in x:
                x = x[0:-1]
                (acc, addr) = x.split(',')
                addrs[acc] = addr
        fr.close()
        return addrs

    def get_pseudonym(self, plain_text):
        res = requests.get(url='%s=%s' % (self.cfg['pseudonymization']['pseudonomizerWebService'], plain_text),
                           timeout=self.cfg['pseudonymization']['timeout'])

        if res.status_code == http.HTTPStatus.OK:
            return json.loads(res.text)['pseudonym']
        else:
            return None

    def get_pseudonyms(self):
        pseudos = dict()
        for prosumer in self.cfg['roles']['prosumers']:
            pseudos[prosumer] = self.get_pseudonym(prosumer)
        pseudos[self.cfg['roles']['dso']] = self.get_pseudonym(self.cfg['roles']['dso'])
        pseudos[self.cfg['roles']['aggregator']] = self.get_pseudonym(self.cfg['roles']['aggregator'])
        pseudos[self.cfg['roles']['marketOperator']] = self.get_pseudonym(self.cfg['roles']['marketOperator'])

        return pseudos

    def get_identifier(self, pseudos, idx):
        if pseudos is None:
            return idx
        else:
            return pseudos[idx]

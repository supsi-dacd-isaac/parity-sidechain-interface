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
        url = '%s=%s' % (self.cfg['pseudonymization']['pseudonomizerWebService'], plain_text)
        self.logger.info('GET: %s' % url)
        res = requests.get(url=url, timeout=self.cfg['pseudonymization']['timeout'])

        try:
            if res.status_code == http.HTTPStatus.OK:
                pseudo = json.loads(res.text)['pseudonym']
                self.logger.info('Pseudonym acquired (%s)' % pseudo)
                return pseudo
            else:
                self.logger.error('Error retrieving the pseudonym from %s, returned status code = %i' % (url, res.status_code))
                return None
        except Exception as e:
            self.logger.error('Unable to get pseudonym from %s' % url)
            self.logger.error('EXCEPTION: %s' % str(e))
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

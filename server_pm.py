
# Importing section
import http
import json
import sys
import argparse
import logging

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from tendo.singleton import SingleInstance

from classes.pm_sidechain_interface import PMSidechainInterface

# --------------------------------------------------------------------------- #
# Functions
# --------------------------------------------------------------------------- #


# Handler request
def handler_class(pmsi_obj, cfg_obj, logger_obj):
    class RequestHandler(BaseHTTPRequestHandler):

        """!
        Constructor
        """
        def __init__(self, *args, **kwargs):
            self.pmsi = pmsi_obj
            self.cfg = cfg_obj
            self.logger = logger_obj
            super(RequestHandler, self).__init__(*args, **kwargs)

        def manage_response(self, status, msg):
            self.send_response(status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(msg, 'utf8'))

        """!
        Catch a GET request
        """
        def do_GET(self):
            if 'checkTx' in self.path:
                req_status, req_data = self.pmsi.check_tx(self.path.split('/')[-1])
                req_data = json.dumps({'code': req_data}, indent=2)
            elif 'account' in self.path:
                req_status = http.HTTPStatus.OK
                req_data = json.dumps(self.pmsi.get_account_info(), indent=2)
            elif 'energyPrices' in self.path:
                req_status = http.HTTPStatus.OK
                req_data = json.dumps(self.pmsi.calc_forecast_energy_prices(), indent=2)
            else:
                req_status, req_data = self.pmsi.do_query(self.path)

            self.logger.info('GET %s?%s HTTP/1.1" %i' % (urlparse(self.path).path, urlparse(self.path).query, req_status))

            self.manage_response(req_status, str(req_data))

        """!
        Catch a POST request
        """
        def do_POST(self):
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            data_string = data_string.decode('UTF-8')

            # Check if the transaction is related to tokens management
            if 'Tokens' in self.path:
                req_status, tx_hash, msg = pmsi.do_token_transaction(self.path, json.loads(data_string))
            else:
                req_status, tx_hash, msg = pmsi.do_application_transaction(self.path, json.loads(data_string))

            logger.info('POST %s?%s HTTP/1.1" %i' % (urlparse(self.path).path, urlparse(self.path).query, req_status))

            self.manage_response(req_status, json.dumps({'tx_hash': tx_hash, 'msg': msg}))

    return RequestHandler


#  Main
if __name__ == "__main__":
    # get input arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='configuration file')
    arg_parser.add_argument('-l', help='log file')

    args = arg_parser.parse_args()
    cfg = json.loads(open(args.c).read())

    # set logging object
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not args.l:
        log_file = None
    else:
        log_file = args.l

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(threadName)s::%(levelname)s::%(funcName)s::%(message)s',
                        level=logging.INFO, filename=log_file)

    logger.info('Starting program')

    pmsi = PMSidechainInterface(cfg, logger, True)

    # REST server thread
    HandlerClass = handler_class(pmsi, cfg, logger)
    httpd = HTTPServer((cfg['server']['host'], cfg['server']['port']), HandlerClass)

    # Try to launch the server
    try:
        logging.info('Server up on socket %s:%i' % (cfg['server']['host'], cfg['server']['port']))
        httpd.serve_forever()
    except Exception as e:
        logger.error('EXCEPTION: %s' % str(e))
        logger.info('Exit program')



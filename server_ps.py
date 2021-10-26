
# Importing section

import json
import sys
import subprocess
import argparse
import logging

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib import parse
from http import HTTPStatus
from tendo.singleton import SingleInstance

from classes.cosmos_interface import CosmosInterface

# --------------------------------------------------------------------------- #
# Functions
# --------------------------------------------------------------------------- #


# Handler request
def handler_class(ci_obj, cfg_obj, logger_obj):
    class RequestHandler(BaseHTTPRequestHandler):

        """!
        Constructor
        """
        def __init__(self, *args, **kwargs):
            self.ci = ci_obj
            self.cfg = cfg_obj
            self.logger = logger_obj
            self.LOCAL_CMDS = ['/get_tokens_amount', '/getMeasure']
            super(RequestHandler, self).__init__(*args, **kwargs)

        def do_local_cmd(self, cmd):
            result = subprocess.check_output(cmd, shell=True)
            decoded_ret = result.decode('UTF-8')
            # Build the dataset
            res = ''
            for elem in decoded_ret:
                res = '%s%s' % (res, elem)
            return json.loads(res)

        def manage_transaction(self, cmd, params):
            try:
                ci.do_transaction(cmd=cmd, params=params)
                return HTTPStatus.OK
            except Exception as e:
                self.logger.error('EXCEPTION %s' % str(e))
                return HTTPStatus.INTERNAL_SERVER_ERROR

        def get_tokens_amount(self):
            data = ci.get_account_info()
            cmd = '%s/bin/%s query account %s' % (self.cfg['cosmos']['goRoot'], '%scli' % self.cfg['cosmos']['app'],
                                                  data['address'])

            raw_data = subprocess.check_output(cmd, shell=True)
            data = json.loads(raw_data.decode('utf-8'))

            for coin in data['value']['coins']:
                if coin['denom'] == self.cfg['cosmos']['token']:
                    return json.dumps(coin), HTTPStatus.OK
            return None, HTTPStatus.NOT_FOUND

        """!
        Catch a GET request
        """
        def do_GET(self):
            if urlparse(self.path).path in self.LOCAL_CMDS:
                if urlparse(self.path).path == '/get_tokens_amount':
                    data, http_status = self.get_tokens_amount()
                elif urlparse(self.path).path == '/getMeasure':
                    pars = dict(parse.parse_qsl(urlparse(self.path).query))
                    http_status, data = self.ci.do_query(cmd=urlparse(self.path).path.replace('/', ''), params=pars)
                else:
                    data = None
                    http_status = HTTPStatus.NOT_FOUND

            else:
                http_status, data = self.ci.do_query(cmd=urlparse(self.path).path.replace('/', ''), params={})

            self.send_response(http_status)
            self.logger.info('GET %s?%s HTTP/1.1" %i' % (urlparse(self.path).path, urlparse(self.path).query, http_status))

            # send the response
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(str(data), 'utf8'))

        """!
        Catch a POST request
        """
        def do_POST(self):
            app_cli = '%scli' % cfg['cosmos']['app']

            cmd = urlparse(self.path).path.replace('/', '')

            if cmd == 'setAdmin':
                data = dict(parse.parse_qsl(urlparse(self.path).query))
                http_status = self.manage_transaction(cmd, {'address': data['id']})

            if cmd == 'meterAccount':
                data = dict(parse.parse_qsl(urlparse(self.path).query))

                real_cmd = '%s/bin/%s keys show %s' % (self.cfg['cosmos']['goRoot'], app_cli, data['id'])
                data_key = self.do_local_cmd(real_cmd)
                http_status = self.manage_transaction(cmd, {'meter': data_key['name'], 'account': data_key['address']})

            if cmd == 'parameters':
                params = dict(parse.parse_qsl(urlparse(self.path).query))
                http_status = self.manage_transaction(cmd, params)

            if cmd == 'setMeasure':
                params = dict(parse.parse_qsl(urlparse(self.path).query))
                http_status = self.manage_transaction(cmd, params)

            self.send_response(http_status)
            logger.info('POST %s?%s HTTP/1.1" %i' % (urlparse(self.path).path, urlparse(self.path).query, http_status))

            # send the response
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # self.wfile.write(bytes(str(data), 'utf8'))

    return RequestHandler


#  Main
if __name__ == "__main__":
    # Check if another instance is already running
    try:
        singleton = SingleInstance()
    except:
        sys.exit()

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

    ci = CosmosInterface(app=cfg['cosmos']['app'], cfg=cfg, logger=logger)

    # REST server thread
    HandlerClass = handler_class(ci, cfg, logger)
    httpd = HTTPServer((cfg['server']['host'], cfg['server']['port']), HandlerClass)

    # Try to launch the server
    try:
        logging.info('Server up on socket %s:%i' % (cfg['server']['host'], cfg['server']['port']))
        httpd.serve_forever()
    except Exception as e:
        logger.error('EXCEPTION: %s' % str(e))
        logger.info('Exit program')



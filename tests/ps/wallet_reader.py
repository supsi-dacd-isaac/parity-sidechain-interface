# Importing section
import json
import requests

from http import HTTPStatus

#  Main
if __name__ == "__main__":

    # Get the identifier
    cmd = 'get_tokens_amount'
    print('GET COMMAND: %s' % cmd)
    r = requests.get('http://localhost:9119/%s' % cmd)
    print('RESPONSE STATUS %i' % r.status_code)

    if r.status_code == HTTPStatus.OK:
        data = json.loads(r.text)
        print('RESPONSE DATA %s' % data)




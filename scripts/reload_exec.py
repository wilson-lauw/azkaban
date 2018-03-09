#!/usr/bin/python

import requests
import json
import sys

def reload_exec(local=False):
    url = 'http://web.default.svc.cluster.local'
    if local:
        url = 'http://localhost:8081'
    payload = {'action': 'login', 'username': 'admin', 'password': 'admin'}

    r = requests.post(url, data=payload)
    print r.status_code
    print r.text

    session_id = json.loads(r.text)['session.id']
    payload = {'session.id': session_id, 'ajax': 'reloadExecutors'}

    r = requests.post(url + '/executor', data=payload)
    print r.status_code
    print r.text

if __name__ == "__main__":
    if len(sys.argv) > 0:
        reload_exec(local=True)
    else:
        reload_exec()
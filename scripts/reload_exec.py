#!/usr/bin/python

import requests
import json

def reload_exec():
    url = 'http://web.default.svc.cluster.local'
    payload = {'action': 'login', 'username': 'admin', 'password': 'iamadminletmein'}

    r = requests.post(url, data=payload)
    print r.status_code
    print r.text

    session_id = json.loads(r.text)['session.id']
    payload = {'session.id': session_id, 'ajax': 'reloadExecutors'}

    r = requests.post(url + '/executor', data=payload)
    print r.status_code
    print r.text

if __name__ == "__main__":
    reload_exec()
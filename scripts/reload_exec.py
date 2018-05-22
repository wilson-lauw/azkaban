#!/usr/bin/python

import requests
import sys
import time
from wait_for_port_ready import wait_for_port_ready
from get_azk_creds import get_password
import traceback

def reload_exec(local=False):

    retries = 0
    retry_count = 15
    success = False
    while not success:
        try:
            url = 'http://web.default.svc.cluster.local'
            if local:
                url = 'http://localhost:8081'
                wait_for_port_ready(8081, 15)
            payload = {'action': 'login', 'username': 'admin', 'password': get_password('admin')}

            r = requests.post(url, data=payload, timeout=5)
            print r.status_code
            print r.text

            session_id = r.json()['session.id']
            payload = {'session.id': session_id, 'ajax': 'reloadExecutors'}

            r = requests.post(url + '/executor', data=payload, timeout=5)
            print r.status_code
            print r.text

            if r.json()['status'] == 'success':
                success = True

            if not success:
                raise Exception('Reload executors failed')
        
        except Exception as ex:
            print(traceback.format_exc())
            sys.stdout.flush()
            
            retries += 1
            if retries > retry_count:
                return success
            print 'waiting for 1 seconds...'
            time.sleep(1)

    return success


if __name__ == "__main__":
    if len(sys.argv) > 1:
        reload_exec(local=True)
    else:
        reload_exec()
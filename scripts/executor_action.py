#!/usr/bin/python

import requests
import sys
import time
from wait_for_port_ready import wait_for_port_ready
import traceback

action = sys.argv[1]

assert action in ('activate','deactivate')

wait_for_port_ready(12321, 15)

retries = 0
retry_count = 15
success = False

while not success:
    try:
        url = 'http://localhost:12321/executor?action={action}'.format(action=action)

        r = requests.get(url, timeout=5)
        print r.status_code
        print r.text

        if r.json()['status'] == 'success':
            success = True

        if not success:
            raise Exception('Attempt to ' + action + ' executor failed')

    except Exception as ex:
        print(traceback.format_exc())
        sys.stdout.flush()

        retries += 1
        if retries > retry_count:
            sys.exit(1)
        print 'waiting for 1 seconds...'
        time.sleep(1)

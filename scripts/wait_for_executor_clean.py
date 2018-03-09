#!/usr/bin/python

import socket
import requests
import time

URL = 'http://localhost:12321/serverStatistics'

def get_num_assigned_flow():
    resp = requests.get(URL)
    return int(resp.json()['numberOfAssignedFlows'])

result = get_num_assigned_flow()
clean = False
retries = 0
while not clean:
    if result == 0:
        print 'numberOfAssignedFlows: ' + str(result)
        print 'Executor ' + socket.gethostbyname(socket.gethostname()) + ' clean'
        clean = True
    else:
        print 'numberOfAssignedFlows: ' + str(result)
        retries += 1
        if retries > 60:
            sys.exit(1)
        print 'waiting for 10 seconds...'
        time.sleep(10)
        result = get_num_assigned_flow()
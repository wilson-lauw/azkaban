#!/usr/bin/python

import socket
import requests
import time

URL = 'http://localhost:12321/serverStatistics'

def get_num_assigned_flow():
    resp = requests.get(URL, timeout=5)
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
        if retries > 600:
            sys.exit(1)
        print 'waiting for 1 seconds...'
        time.sleep(1)
        result = get_num_assigned_flow()
        
time.sleep(10)

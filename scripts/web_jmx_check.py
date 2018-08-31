#!/usr/bin/python3

import requests
import time
from get_azk_creds import get_password

url = 'http://localhost:8081'
payload = {'action': 'login', 'username': 'admin', 'password': get_password('admin')}

r = requests.post(url, data=payload, timeout=5)
print(r.status_code)
print(r.text)

cookies = r.cookies

url = 'http://localhost:8081/jmx?ajax=getAllMBeanAttributes&mBean=azkaban.jmx.JmxExecutorManager%3Aname%3DexecutorManager'
r = requests.get(url, cookies=cookies, timeout=5)
print(r.status_code)
r = r.json()['attributes']

timestamp_to_be_checked = [r['LastSuccessfulExecutorInfoRefresh'], r['LastThreadCheckTime']]
time_now = time.time()*1000
threshold = 10 * 60000 #10 minutes

for ts in timestamp_to_be_checked:
    lag = time_now - ts
    print('Time lag:', lag)
    assert lag < threshold

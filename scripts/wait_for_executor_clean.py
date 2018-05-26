#!/usr/bin/python3

import socket
import requests
import time
import urllib
from subprocess import check_output
from get_azk_creds import get_password

URL = 'http://localhost:12321/serverStatistics'
web_url = 'http://web.default.svc.cluster.local'

def get_num_assigned_flow():
    resp = requests.post(URL, timeout=5)
    return int(resp.json()['numberOfAssignedFlows'])

def get_running_flows_from_web(this_executor_id, cookies):
    url = web_url + '/executor'
    result = requests.get(url, cookies=cookies, timeout=5)
    result = result.text
    result = result.split('killFlow(')[:-1]
    flows = {}
    for r in result:
        start = r.index('<a href="/executor?execid=') + len('<a href="/executor?execid=')
        end = r.index('">', start)
        execution_id = int(r[start:end])
        start = r.index('<td>', end) + len('<td>')
        end = r.index('</td>', start)
        executor_id = int(r[start:end].replace(' ','').replace('\n',''))
        if executor_id == this_executor_id:
            start = r.index('"/manager?') + len('"/manager?')
            end = r.index('">', start)
            result = r[start:end].split('&')
            flows[execution_id] = {}
            for r in result:
                kv = r.split('=')
                flows[execution_id][kv[0]] = kv[1]

    return flows

start = time.time()

cmd = 'cat /yaml/exec.yaml|grep terminationGracePeriodSeconds'
grace_period = int(check_output(cmd, shell=True).replace('terminationGracePeriodSeconds:','').rstrip().lstrip())

result = get_num_assigned_flow()
clean = False
retries = 0

while not clean:
    if result == 0:
        print('numberOfAssignedFlows: ' + str(result))
        print('Executor ' + socket.gethostbyname(socket.gethostname()) + ' clean')
        clean = True
    else:
        print('numberOfAssignedFlows: ' + str(result))
        retries += 1
        if retries > grace_period - 600:
            break
        print('waiting for 1 seconds...')
        time.sleep(1)
        result = get_num_assigned_flow()
        now = time.time()
        elapsed = now - start
        remaining_time = grace_period - 600 - elapsed
        if remaining_time <= result * 2:
            break

if not clean:
    ## check for flows that are still running and kill it
    url = 'http://localhost:12321/executor?action=getStatus'
    resp = requests.post(url, timeout=5)
    this_executor_id = int(resp.json()['executor_id'])

    payload = {'action': 'login', 'username': 'admin', 'password': get_password('admin')}
    r = requests.post(web_url, data=payload, timeout=5)
    print(r.status_code)
    print(r.text)
    session_id = r.json()['session.id']
    cookies = r.cookies

    flows = get_running_flows_from_web(this_executor_id, cookies)

    # kill the flows
    for id in flows.keys():
        url = web_url + '/executor?ajax=cancelFlow&execid=' + str(id)
        print('killing execution id ' + str(id) + \
                requests.get(url, cookies=cookies, timeout=5).text)

    # wait for executor clean
    result = len(get_running_flows_from_web(this_executor_id, cookies))
    clean = False
    retries = 0

    while not clean:
        if result == 0:
            print('running flows: ' + str(result))
            print('Executor ' + socket.gethostbyname(socket.gethostname()) + ' clean')
            clean = True
        else:
            print('running flows: ' + str(result))
            retries += 1
            if retries > 10:
                break
            print('waiting for 1 seconds...')
            time.sleep(1)
            result = len(get_running_flows_from_web(this_executor_id, cookies))

    # grab info for the flow
    submit_first = []
    submit_second = []
    for id in flows.keys():
        url = web_url + '/executor?ajax=flowInfo&execid=' + str(id)
        print('getting flow info for execution id ' + str(id))
        result = requests.get(url, cookies=cookies, timeout=5)
        flows[id]['info'] = result.json()
        if flows[id]['info']['concurrentOptions'] == 'skip':
            submit_first.append(id)
        else:
            submit_second.append(id)
            
    # resubmit flows
    for execution_id in submit_first + submit_second:
        execution_info = flows[execution_id]
        flow_override = []
        for k,v in execution_info['info']['flowParam'].iteritems():
            flow_override.append(urllib.quote('flowOverride[{k}]'.format(k=k)) + \
                '={v}'.format(v=v))
        flow_override = '&' + '&'.join(flow_override) if len(flow_override) > 0 else ''
        disabled = []
        for k,v in execution_info['info']['nodeStatus'].iteritems():
            if v not in ('KILLED', 'CANCELLED'):
                disabled.append(str(k))
        url = '''
        {web_url}/executor?project={project}&ajax=executeFlow&flow={flow}&disabled={disabled}&
        failureEmailsOverride={failureEmailsOverride}&successEmailsOverride={successEmailsOverride}&
        failureAction={failureAction}&failureEmails={failureEmails}&successEmails={successEmails}&
        notifyFailureFirst={notifyFailureFirst}&notifyFailureLast={notifyFailureLast}&
        concurrentOption={concurrentOption}
        '''.format(
            web_url=web_url,
            project = execution_info['project'],
            flow=execution_info['flow'],
            disabled=urllib.quote(str(disabled).replace("'",'"')),
            failureEmailsOverride=execution_info['info']['failureEmailsOverride'],
            successEmailsOverride=execution_info['info']['successEmailsOverride'],
            failureAction=execution_info['info']['failureAction'],
            failureEmails=urllib.quote_plus(','.join(execution_info['info']['failureEmails'])),
            successEmails=urllib.quote_plus(','.join(execution_info['info']['successEmails'])),
            notifyFailureFirst=execution_info['info']['notifyFailureFirst'],
            notifyFailureLast=execution_info['info']['notifyFailureLast'],
            concurrentOption=execution_info['info']['concurrentOptions']
        )
        url = url.replace('\n','').replace(' ','') + flow_override
        print(url)
        result = requests.get(url, cookies=cookies, timeout=5)
        print(result.text)
    
## allow for notifications
time.sleep(10)

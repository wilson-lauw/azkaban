#!/usr/bin/python3

from subprocess import getoutput
import mysql_util
from reload_exec import reload_exec
from wait_for_port_ready import wait_for_port_ready
import time
import requests
import traceback
import sys

def check_exec_pods_stability():
    cmd = 'kubectl get po -o wide|grep exec|grep 2/2|grep Running|wc -l'
    num_stable_pods = int(getoutput(cmd))

    cmd = "kubectl get po -o wide|grep exec|grep -v Evicted|grep -Ev '0/2.*Terminating'|wc -l"
    num_all_pods = int(getoutput(cmd))

    stable = num_stable_pods == num_all_pods
    return stable

def clean_evicted_pods():
    cmd = "kubectl get po|grep Evicted|awk '{print $1}'"
    result = getoutput(cmd).split('\n')
    result = filter(lambda l:len(l) > 0, result)
    for pod in result:
        print('cleaning pod', r)
        cmd = 'kubectl delete po {} --force --grace-period=0'.format(pod)
        print(getoutput(cmd))

def clean_terminating_pods():
    cmd = "kubectl get po|grep Terminating|grep 0/2|awk '{print $1}'"
    result = getoutput(cmd).split('\n')
    result = filter(lambda l:len(l) > 0, result)
    for pod in result:
        print('cleaning pod', r)
        cmd = 'kubectl delete po {} --force --grace-period=0'.format(pod)
        print(getoutput(cmd))
    
# copy config file
cmd = 'cp /secrets/azkaban-properties/azkaban.properties /azkaban/conf'
print(getoutput(cmd))
cmd = 'cp /secrets/azkaban-users-xml/azkaban-users.xml /azkaban/conf'
print(getoutput(cmd))

# activate service account and kubectl
cmd = 'gcloud auth activate-service-account --key-file=/secrets/cloudsql/credentials.json'
print(getoutput(cmd))
cmd = 'gcloud container clusters get-credentials azkaban-cluster --zone asia-southeast1-a --project [project-id]'
print(getoutput(cmd))

wait_for_port_ready(3306, 15)
wait_for_port_ready(8081, 45)

while True:
    time.sleep(60)
    
    try:
        # reload executors
        print('reload executors..')
        reload_exec(True)

        print('cleaning evicted pods..')
        clean_evicted_pods()

        print('cleaning terminating pods..')
        clean_terminating_pods()
        
        # wait for pods are stable
        stable = check_exec_pods_stability()
        while not stable:
            print("Pods are not stable yet...")
            print('waiting for 10 seconds...')
            time.sleep(10)
            stable = check_exec_pods_stability()

        print("Pods are stable")

        start = time.time()

        cmd = 'cat /azkaban/conf/azkaban.properties|grep mysql.host'
        host = getoutput(cmd).replace('mysql.host=','').rstrip()

        cmd = 'cat /azkaban/conf/azkaban.properties|grep mysql.database'
        db = getoutput(cmd).replace('mysql.database=','').rstrip()

        cmd = 'cat /azkaban/conf/azkaban.properties|grep mysql.user'
        user = getoutput(cmd).replace('mysql.user=','').rstrip()

        cmd = 'cat /azkaban/conf/azkaban.properties|grep mysql.password'
        passwd = getoutput(cmd).replace('mysql.password=','').rstrip()

        # grab executors list from db
        sql = 'select host from executors'
        from_db = mysql_util.mysql_fetch(sql, host, user, passwd, db)
        executors_in_db = []
        for row in from_db:
            executors_in_db.append(row['host'])
        executors_in_db = set(executors_in_db)
        print('executors_in_db:', executors_in_db)

        # grab executors list from kubectl
        cmd = "kubectl get po -o wide|grep exec|grep 2/2|grep Running|awk '{print $6}'"
        result = getoutput(cmd).split('\n')
        result = filter(lambda l:len(l) > 0, result)
        executors_in_kube = []
        for r in result:
            executors_in_kube.append(r)
        executors_in_kube = set(executors_in_kube)
        print('executors_in_kube:', executors_in_kube)

        if executors_in_db != executors_in_kube:
            print('executors list inconsistent..!!')
            print('purging list from db...')
            sql = 'TRUNCATE TABLE executors'
            mysql_util.mysql_execute(sql, host, user, passwd, db)
            print('populating db...')
            if len(executors_in_kube) > 0:
                values = []
                for current_host in executors_in_kube:
                    values.append("('{current_host}',12321, true)".format(current_host=current_host))
                sql = 'INSERT INTO executors (host, port, active) VALUES ' + ','.join(values)
                mysql_util.mysql_execute(sql, host, user, passwd, db)

                # reload executors
                print('reload executors after db sync..')
                reload_exec(True)

        else:
            print('executors list consistent')

        # grab executors from web server
        URL = 'http://web.default.svc.cluster.local/status'
        resp = requests.get(URL, timeout=5)
        executorStatusMap = resp.json()['executorStatusMap']
        registered_executors = []

        for id, execInfo in executorStatusMap.items():
            host = execInfo['host']
            registered_executors.append(host)

        registered_executors = set(registered_executors)
        print('registered_executors:', registered_executors)

        if registered_executors != executors_in_kube:
            print('second layer reload executors...')
            reload_exec(True)

        else:
            print('registered executors list consistent')

        end = time.time()
        print('Elapsed: ' + str((end-start) * 1000) + ' ms')
        sys.stdout.flush()

    except Exception as ex:
        print(traceback.format_exc())
        sys.stdout.flush()

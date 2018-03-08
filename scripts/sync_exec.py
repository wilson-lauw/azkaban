#!/usr/bin/python

from subprocess import check_output
import socket
import time
import sys
import mysql_util
from reload_exec import reload_exec
from wait_for_port_ready import wait_for_port_ready
import time

start = time.time()

# activate service account and kubectl
cmd = 'gcloud auth activate-service-account --key-file=/secrets/cloudsql/credentials.json'
print check_output(cmd, shell=True)
cmd = 'gcloud container clusters get-credentials azkaban --zone asia-east1-a --project [project-id]'
print check_output(cmd, shell=True)

wait_for_port_ready(3306, 5, 3)

cmd = 'cat /common/conf/azkaban.properties|grep mysql.password'
passwd = check_output(cmd, shell=True).replace('mysql.password=','').rstrip()

# wait for pods are stable
def check_exec_pods_stability():
    cmd = 'kubectl get po -o wide|grep exec|grep 2/2|grep Running|wc -l'
    num_stable_pods = int(check_output(cmd, shell=True))

    cmd = 'kubectl get po -o wide|grep exec|wc -l'
    num_all_pods = int(check_output(cmd, shell=True))

    stable = num_stable_pods == num_all_pods
    return stable

stable = check_exec_pods_stability()
retries = 0
while not stable:
    print "Pods are not stable yet..."
    retries += 1
    if retries > 60:
        sys.exit(1)
    print 'waiting for 10 seconds...'
    time.sleep(10)
    stable = check_exec_pods_stability()

print "Pods are stable"

# grab executors list from db
sql = 'select host from executors'
from_db = mysql_util.mysql_fetch(sql, '127.0.0.1', 'root', passwd, 'azkaban')
executors_in_db = []
for row in from_db:
    executors_in_db.append(row['host'])
executors_in_db = set(executors_in_db)
print executors_in_db

# grab executors list from kubectl
cmd = "kubectl get po -o wide|grep exec|grep 2/2|grep Running|awk '{print $6}'"
result = check_output(cmd, shell=True).split('\n')
result = filter(lambda l:len(l) > 0, result)
executors_in_kube = []
for r in result:
    executors_in_kube.append(r)
executors_in_kube = set(executors_in_kube)
print executors_in_kube

if executors_in_db != executors_in_kube:
    print 'executors list inconsistent..!!'
    print 'purging list from db...'
    sql = 'TRUNCATE TABLE executors'
    mysql_util.mysql_execute(sql, '127.0.0.1', 'root', passwd, 'azkaban')
    print 'populating db...'
    if len(executors_in_kube) > 0:
        values = []
        for host in executors_in_kube:
            values.append("('{host}',12321)".format(host=host))
        sql = 'INSERT INTO executors (host, port) VALUES ' + ','.join(values)
        mysql_util.mysql_execute(sql, '127.0.0.1', 'root', passwd, 'azkaban')

    # reload executors
    print 'reload executors'
    reload_exec()

else:
    print 'executors list consistent'

end = time.time()
print('Elapsed: ' + str((end-start) * 1000) + ' ms')

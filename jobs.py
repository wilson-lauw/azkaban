#!/usr/bin/python

from azkaban import Job, Project
from azkaban.remote import Session
import os
from glob import glob

cwd = os.getcwd()

def list_files(PATH=cwd):
    result = [y for x in os.walk(PATH) for y in glob(os.path.join(x[0], '*.*'))]
    return result

PROJECT_NAME = 'test_project'
print 'building...'
project = Project(PROJECT_NAME)
for f in list_files(cwd + '/test_folder'):
    project.add_file(f, f.replace(cwd, ''))

project.properties = {'retries': 1, 'retry.backoff':60000}
flows = []

for j in xrange(1,2):
    project.add_job(str(j) + '_' + str(0), Job({'type': 'command', 'command': 'sleep 1'}))
    for i in xrange(1,5):
        project.add_job(str(j) + '_' + str(i), Job({'type': 'command', 'command': 'echo gg', 'dependencies':str(j) + '_' + str(i-1)}))
    flows.append(str(j) + '_' + str(4))

path = cwd + '/result.zip'
project.build(path, overwrite=True)
print 'build complete'

print 'uploading...'
session = Session('http://admin:iamadminletmein@localhost:8081')
session.upload_project(PROJECT_NAME, path)
print 'upload complete'

print 'scheduling...'
option = {'concurrent':'skip', 'on_failure':'continue',
          'notify_early':True, 'emails': (['gg@gg.com'],[])}
for f in flows:
    print 'scheduling ' + f
    session.schedule_workflow(PROJECT_NAME, f, '01/01/2018', '0,0,AM,PDT', '5m', **option)
print 'schedule complete'






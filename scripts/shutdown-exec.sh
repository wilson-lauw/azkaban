#!/usr/bin/env bash

/scripts/executor_action.py deactivate
/scripts/reload_exec.py
/scripts/wait_for_executor_clean.py
/azkaban-exec-server/bin/shutdown-exec.sh
touch /tmp/pod/main-terminated
kill $(ps aux|grep "tail -f /dev/null"|grep -v grep|awk '{print $2}')

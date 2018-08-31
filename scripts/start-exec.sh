#!/usr/bin/env bash

/scripts/wait_for_port_ready.py 3306 15
/azkaban-exec-server/bin/start-exec.sh
/scripts/wait_for_port_ready.py 12321 15
/scripts/executor_action.py activate
/scripts/reload_exec.py
tail -f /dev/null
#!/usr/bin/env bash

/scripts/wait_for_port_ready.py 3306 5 3
/azkaban-exec-server/bin/start-exec.sh
/scripts/wait_for_port_ready.py 12321 1 15
curl "localhost:12321/executor?action=activate"
/scripts/reload_exec.py
tail -f /dev/null
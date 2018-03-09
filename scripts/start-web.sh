#!/usr/bin/env bash

/scripts/wait_for_port_ready.py 3306 5 3
/azkaban-web-server/bin/start-web.sh
/scripts/wait_for_port_ready.py 8081 5 3
/scripts/reload_exec.py
tail -f /dev/null
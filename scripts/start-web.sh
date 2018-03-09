#!/usr/bin/env bash

/scripts/wait_for_port_ready.py 3306 15
/azkaban-web-server/bin/start-web.sh
/scripts/wait_for_port_ready.py 8081 15
/scripts/reload_exec.py
tail -f /dev/null
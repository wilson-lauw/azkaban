#!/usr/bin/env bash

/scripts/wait_for_port_ready.py 3306 15
/azkaban-web-server/bin/start-web.sh
/scripts/reload_exec.py local
tail -f /dev/null
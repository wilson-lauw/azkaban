#!/usr/bin/env bash

/scripts/wait_for_port_ready.py 3306 5 3
/azkaban-web-server/bin/start-web.sh 
tail -f /dev/null
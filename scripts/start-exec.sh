#!/usr/bin/env bash

cp /secrets/azkaban-properties/azkaban.properties /azkaban/conf
cp /secrets/azkaban-users-xml/azkaban-users.xml /azkaban/conf
/scripts/wait_for_port_ready.py 3306 15
/azkaban/bin/start-exec.sh
/scripts/wait_for_port_ready.py 12321 15
/scripts/executor_action.py activate
/scripts/reload_exec.py
tail -f /dev/null
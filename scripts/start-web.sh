#!/usr/bin/env bash

cp /secrets/azkaban-properties/azkaban.properties /azkaban/conf
cp /secrets/azkaban-properties/azkaban-users.xml /azkaban/conf
/scripts/wait_for_port_ready.py 3306 30
/azkaban-web-server/bin/start-web.sh
/scripts/wait_for_port_ready.py 8081 45
/scripts/reload_exec.py local
tail -f /dev/null
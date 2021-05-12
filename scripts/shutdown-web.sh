#!/usr/bin/env bash

/azkaban/bin/shutdown-web.sh
touch /tmp/pod/main-terminated
kill $(ps aux|grep "tail -f /azkaban/webServerLog_"|grep -v grep|awk '{print $2}')

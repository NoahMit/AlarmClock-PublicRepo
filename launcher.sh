#!/bin/sh
# launcher.sh
# IF PI REBOOTS, RELAUNCH EVERYTHING
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/alarm_app
nohup yarn start-api>backend.out & nohup yarn start>frontend.out &
(sleep 30 && curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://ip.address:5000/setalarmclock)&
cd /

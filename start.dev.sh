#!/bin/bash
nohup python ./xcms.py --port=8080 > dev.log 2 >&1&
PID1=$! 
nohup python ./xcms.py --port=8081 > dev.log 2 >&1&
PID2=$!
echo $PID1 $PID2 > dev.pid


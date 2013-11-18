#!/bin/bash
PIDS=$(cat ./dev.pid)
kill $PIDS

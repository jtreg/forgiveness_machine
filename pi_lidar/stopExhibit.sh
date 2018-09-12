#!/bin/bash
# James Tregaskis August 2018
# Part of the installation for final year project
#

P1=$!
ps -e | awk '$4~/java/{print $1}' | xargs kill
ps -e | awk '$4~/python3/{print $1}' | xargs kill

python3  ~/python/osc/stop_display.py &
P2=$!
wait $P1 $P2

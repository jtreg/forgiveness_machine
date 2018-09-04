#!/bin/bash



#/home/pi/python/osc/processingReceiveTest/application.linux-arm64/processingReceiveTest


#home/pi/python/osc/processingReceiveTestb/application.linux-arm64/processingReceiveTestb &&

#1=$!
#hile 1: do
#python3  ~/python/osc/display_servos.py &
less ~/python/osc/displayservosPID | awk $1 | echo
    #sleep 4
    #s -e | awk '$4~/python3/{print $1}' | xargs kill
#one
P2=$!
wait $P1 $P2
        

#!/bin/bash
# James Tregaskis August 2018
# Part of the installation for final year project
#
# this will start the exhibition piece in stand-alone Model
# as the interaction has problems running beyond 10 minutes
# better to have it running 'random' instead.


/home/pi/python/osc/processingReceiveTestb/application.linux-arm64/processingReceiveTestb &
#/home/pi/python/osc/processingReceiveTestb/application.linux-arm64
time 2

python3  ~/python/osc/display_servos.py &
time 5

#!/bin/bash
# this starts up the installation and runs it in interactive mode ;
# the alternative would be to run startExhibit2.sh as it runs in non-interactive n
# mode, providing a more stable setup (used to run installation over a day)


#/home/pi/python/osc/processingReceiveTest/application.linux-arm64/processingReceiveTest


/home/pi/python/osc/processingReceiveTestb/application.linux-arm64/processingReceiveTestb &
#/home/pi/python/osc/processingReceiveTestb/application.linux-arm64
time 2
# this bash script can run another python script to recycle the display_servos.py program
python3 ~/runpython.py ~/python/osc/display_servos.py

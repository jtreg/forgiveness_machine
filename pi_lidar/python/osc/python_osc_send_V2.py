"""
Title:
python_osc_send_v2.py

# Part of the installation for final year project
#
Description:
RoboPeak Lidar sensor runs to collect
angle and distance data of reflected objects
This is in turn sent to another Raspberry Pi, using Open Sound control
(OSC)

Part of work for final project
MA Computational Art
2018
Version 0.2

Author:
james@tregaskis.org
Date:
August 2018

Credits:
code adapted from
https://pypi.org/project/python-osc/
and
https://github.com/SkoltechRobotics/rplidar

"""
import argparse
import random
import time
import sys

from rplidar import RPLidar

from pythonosc import osc_message_builder
from pythonosc import udp_client
PORT_NAME = '/dev/ttyUSB0'

lidar = RPLidar(PORT_NAME)

lidar.stop()
lidar.clear_input()

#Added this delay avoid Lidar throwing Incorrect descriptor me ssage and failing
time.sleep(2)
#################################################################
info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)
ANGLE=2
DISTANCE=3
#2000 prob ok for exhibition, 500 for garage
IGNORE_REDINGS_BEYOND = 4500
PORT_FOR_RECEIVING_MACHINE=5005
try:
    if __name__ == "__main__":
      parser = argparse.ArgumentParser()
      parser.add_argument("--ip", default="10.10.10.1",
          help="The ip of the OSC server")
      parser.add_argument("--port", type=int, default=PORT_FOR_RECEIVING_MACHINE,
          help="The port the OSC server is listening on")
      args = parser.parse_args()
      client = udp_client.SimpleUDPClient(args.ip, args.port)


    distance_old=[None]*361;

    distance_new=[None]*361;
    # this is the important part, to send the polar position data to PI no. 2
    for measurment in lidar.iter_measurments():
        # strength of laser, angle of reading, distance
        #print("ANGLE ",int(measurment[2]))
        #print("DISTANCE", int(measurmen[3])
        if int(measurment[1]) > 0:
            if int(measurment[DISTANCE]) < IGNORE_REDINGS_BEYOND :
                distance_new[int(measurment[ANGLE])] = int(measurment[DISTANCE])
                if distance_new[int(measurment[ANGLE])] != distance_old[int(measurment[ANGLE])] :

                    an = int(measurment[ANGLE])
                    di = int(distance_new[int(measurment[ANGLE])])
                    distance_old[int(measurment[ANGLE])]=distance_new[int(measurment[ANGLE])]
                    print(an,di)
                    distance_new[int(measurment[ANGLE])]=int(measurment[ANGLE])
                    # transmit data using OSC protocol
                    client.send_message("/st", [an, di])
                    ######################################

    time.sleep(1)
except IOError as ioex:
	print (ioex)
	pass
except KeyboardInterrupt:
    print('Ctrl-c pressed, Stopping.')

except Exception as e: print(e)
finally:
    #osc_terminate()
    lidar.stop()
    lidar.disconnect()

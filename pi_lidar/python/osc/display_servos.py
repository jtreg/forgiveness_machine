
'''
Title:

display_servos.py
----------------------

Description:
To run on a Raspberry Pi to control servos and pump.

 I get Open Sound Control data sent from Lidar
 (on another Raspberry Pi Model3 B+)
 I use this program to actuate servos and a L298N
 H Bridge running a medical pump
 using PCA9685 PWM servo/LED controller library and PCA9685
 16 channel I2C motor controllers

Date: August 2018
Author: James Tregaskis
Credits:
 PCA9685 PWM servo/LED controller library by:
 Author: Tony DiCola
 License: Public Domain
 OSC library in Python:
 https://pypi.org/project/python-osc/
 and
 https://github.com/SkoltechRobotics/rplidar
'''

from __future__ import division
import time
from pythonosc import dispatcher
from pythonosc import osc_server
# Import the PCA9685 module.
import Adafruit_PCA9685
import argparse
import math
import random
import asyncio
from threading import Thread
import os
import sys
# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm1 = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
pwm2 = Adafruit_PCA9685.PCA9685(address=0x41, busnum=1)
pwm3 = Adafruit_PCA9685.PCA9685(address=0x43, busnum=1)
pwm4 = Adafruit_PCA9685.PCA9685(address=0x47, busnum=1)
pwm5 = Adafruit_PCA9685.PCA9685(address=0x4f, busnum=1)
pwm6 = Adafruit_PCA9685.PCA9685(address=0x70, busnum=1)


# pie slices on N, S, E, W .. .
NW=([5,6,12,15,22,27,21,26,4])
NE=([7,17,23,9])
SW=([11,20,31,3,14,25,36,10])
SE=([34,18,13,1,29,32,20,19,9,2])

# setup tuples to map types
ANEMONES=([11,16,18,26,30])
BANDAGES=([20,24])
BOXES=([6,7,9,22,31,35])
BULBS=([1,4])
CRUCIFIXES=([3,10,12,13,21,28,29])
DOGPOOS=([23,25,32,5])
ROSES=([0,2,8,14,15,17,19,27,33,34])

CONTINUOUS=([30,9,19,21,34,36,29,4,3,10,12,13,20,22,26,28])
NO=([28,5,8,23,35,0,6])

BEATING_HEART=0
JOSETTE_PUMP=48
overall_delay=0

#device_types:
ANEMONE=1
BANDAGE=2
BOX=3
BULB=4
CRUCIFIX=5
DOGPOO=6
ROSE=7
IS_NW=8
IS_NE=9
IS_SE=10
IS_SW=11
CONTINOUS=12

#DISTANCES
VERY_CLOSE = 100
CLOSE = 1500
VERY_NEAR = 2000
OK = 3000
FAR = 4000
VERY_FAR = 5000

# Configure min and max servo pulse lengths
servo_min = 170  # Min pulse length out of 4096
servo_max = 550  # Max pulse length out of 4096

#DEFAULT_RUNNING_TIME this is the period that any movement routine repeats itself
# in this design pattern each movement function should not run indefinityly 
# so this default will kick in to run n times accorfing to the enum below.
# the movement functions will accept a parameter to override this default if required.
DEFAULT_RUNNING_TIME = 2


# used in testing and setting up
LIDAR_RECEIVE=1
SERVOS_ON = 1
DEBUG_MODE=0
IP ="10.10.10.1"
PORT_NO=5006
CHANNELS_ON_CARD=16 			
DISTANCE_MAX_SENSED = 5000
SERVO_ON=1
PUMP_ON=1
PUMP_WIRE_NO=80
then  = time.time()
now = time.time()

#State
BUSY=0

dieat = int(time.time())

def lonelyRoutine():
    # nothing happening, no one picked up on lidar
    # 'lonely' with no-one around
        print(" in lonelyRoutine")
        return


def hello():
    print("Hello from timer")

def stopAllServos():
	for i in range(0,45):
		actuateServoFromNum(i, 0)
	

def setDefaultFrequency():
	# Set frequency to 60hz, good for servos.
	#permissable frequency is between 40 and 1000
	_PULSE_RANGE = 60
	pwm1.set_pwm_freq(_PULSE_RANGE)
	pwm2.set_pwm_freq(_PULSE_RANGE)
	pwm3.set_pwm_freq(_PULSE_RANGE)
	pwm4.set_pwm_freq(_PULSE_RANGE)
	pwm5.set_pwm_freq(60) #special for pump
	pwm6.set_pwm_freq(20)

def workPump(power, duration, freq, intensity, runfor=DEFAULT_RUNNING_TIME):
    #try:
        #ran = random.randint(20,50)
        #print(ran)
        #for i in range(1 ,ran):
        #	pwm5.set_pwm_freq(i)
        #pwm5.set_pwm_freq(10)
        #pwm5.set_pwm_freq(10)
    #print("power in " , power)
    BUSY = 1
    if PUMP_ON == 0:
        #pwm5.set_pwm(15, 0, 0)
        return
    else:
        power = valMap(power, 0,intensity, 200, 1200)
        print ("in workPump; power of pump is " , int(power), " duration ", duration)
        while runfor > 0:
            for i in range(0,freq):
                pwm6.set_pwm_freq = i
            pwm5.set_pwm(0, 0, power)
            time.sleep(duration)
                #pwm5.set_pwm(15, 0, 1500)
                #time.sleep(2)
            #except Exception as e: print(e)
            runfor = runfor -1
    BUSY=0
    
def valMap(value, istart, istop, ostart, ostop):
    retVal = ostart + (ostop -ostart) * ((value - istart)/ (istop -istart))
    return int(retVal)




def actuateServoFromNum(num, stopAt, runfor=DEFAULT_RUNNING_TIME):

    if SERVO_ON == 0:
        
        return
    else:
        try:
            
            #print(" actuating device ... " , num)
            if num >= 0 and num < CHANNELS_ON_CARD and runfor > 0:
                #-----------------------------------------------
                # arguments:
                # 1.) channel number
                # 2.) on: the tick between 0 and 4095 when the 
                #     signal should transition fromn low to high.
                # 3.) off: the tiick between 0 and 4095 when the 
                #     signal should transition fromn high to low.
                #------------------------------------------------
                val = num
                if DEBUG_MODE:
                    print ("actuating device on card 1 ", val)
                while runfor > 0:
                    pwm1.set_pwm(num, 0, stopAt)
                    runfor = runfor -1
                    
            elif  num >= CHANNELS_ON_CARD and num < CHANNELS_ON_CARD * 2 and runfor > 0:
                val = num-CHANNELS_ON_CARD
                if DEBUG_MODE:
                    print ("actuating device on card 2 ", val)
                while runfor > 0:
                    pwm2.set_pwm(val, 0, stopAt)
                    runfor = runfor -1

            elif  num >= CHANNELS_ON_CARD * 2  and num < CHANNELS_ON_CARD * 3 and runfor > 0:
                val = num-(CHANNELS_ON_CARD*2)
                if DEBUG_MODE:
                    print ("actuating device on card 3 ", val)
                while runfor > 0:
                    pwm3.set_pwm(val, 0, stopAt)
                    runfor = runfor -1

            elif  num >= CHANNELS_ON_CARD * 3  and num < CHANNELS_ON_CARD * 4 and runfor > 0:
                val = num-(CHANNELS_ON_CARD*3)
                if DEBUG_MODE:
                    print ("actuating device on card 4 ", val)
                while runfor > 0:
                    pwm4.set_pwm(val, 0, stopAt)
                    runfor = runfor -1
            elif  num >= CHANNELS_ON_CARD * 4  and num < CHANNELS_ON_CARD * 5 and runfor > 0:
                val = num-(CHANNELS_ON_CARD*4)
                if DEBUG_MODE:
                    print ("actuating device on card 5 ", val)
                while runfor > 0:
                    pwm5.set_pwm(val, 0, stopAt)
                    runfor = runfor -1

            elif  num >= CHANNELS_ON_CARD * 5  and num < CHANNELS_ON_CARD * 6 and runfor > 0:
                val = num-(CHANNELS_ON_CARD*5)
                if DEBUG_MODE:
                    print ("actuating device on card 6 ", val)
                while runfor > 0:
                    pwm6.set_pwm(val, 0, stopAt)
                    runfor = runfor -1
            if DEBUG_MODE:
                print(num, val)
            
        except Exception as e : print(e)




def moveByGroupType(processedGroup, delay, stopAt):
    #get the list iterate and move them
    for i in processedGroup:
        actuateServoFromNum(i, stopAt)
        time.sleep(delay)

def startContinuousServos():
    for i in CONTINUOUS:
        actuateServoFromNum(i, servo_min)

def stopContinuousServos():
    for i in CONTINUOUS:
        stopOne(i)
        

'''
Coordinates the movement of groups of servos
'''
def choregraphyActioByTypeOfObject(groupOf, delay, stopAt):
    stopContinuousServos()
    if groupOf==CRUCIFIX:
        if DEBUG_MODE:
            print("actuating CRUCIFIXES")
        moveByGroupType(CRUCIFIXES, delay, stopAt)
        
    elif groupOf==DOGPOO:
        if DEBUG_MODE:
            print("actuating DOGPOOS")
        moveByGroupType(DOGPOOS, delay,stopAt)
    elif groupOf==ROSE:
        if DEBUG_MODE:
            print("actuating ROSE")
        moveByGroupType(ROSES, delay,stopAt)
    elif groupOf==BOX:
        if DEBUG_MODE:
            print("actuating BOXES")
        moveByGroupType(BOXES, delay,stopAt)
    elif groupOf==ANEMONE:
        if DEBUG_MODE:
            print("actuating ANEMONES")
        moveByGroupType(ANEMONES, delay,stopAt)
    elif groupOf==IS_NE:
        if DEBUG_MODE:
            print("actuating NE")
        moveByGroupType(NE, delay,stopAt)
    elif groupOf==IS_NW:
        if DEBUG_MODE:
            print("actuating NW")
        moveByGroupType(NW, delay,stopAt)
    elif groupOf==IS_SE:
        if DEBUG_MODE:
            print("actuating SE")
        moveByGroupType(SE, delay,stopAt)
    elif groupOf==IS_SW:
        if DEBUG_MODE:
            print("actuating SW")
        moveByGroupType(SW, delay,stopAt)
    stopContinuousServos()


def distribututeActionByQuadrant(angle, stopAt):
	if angle > 0 and angle <90:
		for a in range(NE):
			actuateServoFromNum(a, stopAt)
	elif angle > 90 and angle < 180:
		for a in range(SE):
			actuateServoFromNum(a, stopAt)
	elif angle > 180 and angle < 270:
		for a in range(SW):
			actuateServoFromNum(a ,stopAt)
	elif angle > 270 and angle < 360:
		for a in range(NW):
			actuateServoFromNum(a, stopAt)

def recordLastSeen():
	global  then
	then = time.time()

def finishedRoutineCleanUp():
    #stopContinuousServos()
    stopEverything()
    BUSY = 0

'''
This function will take the OSC messages
and activate whatever is necessary
This will set the choreography of the pieces
and is fundemental to controlling the
installation's actions
'''
def handlerfunction(a, an,di):
    # Description:
    # ------------
    # Will receive message data unpacked in angle and distance
    # first argument is the name of the message (label)
    # second is angle
    # third is distance
    # this is the basic mode
    #distribututeActionByQuadrant(an, servo_min)
    #print(a, " an " , an, " di ", di)
    #time.sleep(0.1)
    #distribututeActionByQuadrant(an, servo_max)

    DURATION_PUMP = 2.2
    FREQ = 1
    # default for mapping of pump power 
    INTENSITY = 850
    #but we could hook up to the lidar data for this!


    #DISTANCES
    VERY_CLOSE = 100
    CLOSE = 1500
    VERY_NEAR = 2000
    OK = 3000
    FAR = 4000
    VERY_FAR = 5000
    #while  dieat+5.0 -  time.time() > 0:


    try:
        #if not int(dieat+5.0 -  int(time.time())) > 0:
        ##    print("running", int(dieat+5.0 -  time.time()))
        ##else:
            #raise SystemExit
            #os._exit(1)
            ##quit()
        
        # busy now;someone is out there!
        # set this state to ....
        BUSY = 1
        
        if di < DISTANCE_MAX_SENSED and an > 0 and an < 30:
            '''
            VERY_CLOSE = 100
            CLOSE = 1500
            VERY_NEAR = 2000
            OK = 3000
            FAR = 4000
            VERY_FAR = 5000

            '''
            print(" 0-30 " , an, " di ", di)
            if  di < VERY_CLOSE:
                workPump(an+100,DURATION_PUMP, FREQ, an)
            elif  di < CLOSE  and  di > VERY_CLOSE:
                vibrateRoses(3)
            elif  di < VERY_NEAR  and  di > CLOSE:
                vibrateRoses(0)
            elif di < OK:
                vibrateBoxes()
                vibrateRoses(11)
            elif  di < FAR  and  di > OK:
                vibrateRoses(0)
            elif  di < VERY_FAR  and  di > FAR:
                workPump(di+10, DURATION_PUMP, FREQ, an,2)
                vibrateCrucifixes()
         
            
            workPump(an+10,DURATION_PUMP, FREQ, an)
            finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 60 and an < 90:
            if DEBUG_MODE:
                print(" 60 - 90 " , an, " di ", di)
            if  di < VERY_CLOSE:
                workPump(an+10,DURATION_PUMP, FREQ, an)
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print("an >= 60 and an < 90")
            elif  di < VERY_NEAR  and  di > CLOSE:
                print("an >= 60 and an < 90")
            elif di < OK:
                print("an >= 60 and an < 90")
            elif  di < FAR  and  di > OK:
                print("an >= 60 and an < 90")
            elif  di < VERY_FAR  and  di > FAR:
                workPump(an+20,DURATION_PUMP, FREQ, an)
                pulseEverything()
            #for i in range(0 ,10):
            #	actuateServoFromNum(i, servo_min)
            #	time.sleep(0.1)
            #	actuateServoFromNum(i, servo_max))
            finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 90 and an < 120:
            if DEBUG_MODE:
                print(" 90 - 120 " )
            if  di < VERY_CLOSE:
                print(">= 90 and an < 120" )
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print("an >= 60 and an < 90")
            elif  di < VERY_NEAR  and  di > CLOSE:
                print(">= 90 and an < 120" )
            elif di < OK:
                print(">= 90 and an < 120" )
            elif  di < FAR  and  di > OK:
                print(">= 90 and an < 120" )
            elif  di < VERY_FAR  and  di > FAR:
                #stopEverything()
                vibrateRoses(0)
                vibrateBoxes()
                workPump(an+20,DURATION_PUMP, FREQ, an)
            finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 120 and an < 150:
            if DEBUG_MODE:
                print(" 120 - 150 " )
            if  di < VERY_CLOSE:
                print(">= 120 and an < 150" )
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print(">= 120 and an < 150" )
            elif  di < VERY_NEAR  and  di > CLOSE:
                print(">= 120 and an < 150" )
            elif di < OK:
                print(">= 120 and an < 150" )
            elif  di < FAR  and  di > OK:
                print(">= 120 and an < 150" )
            elif  di < VERY_FAR  and  di > FAR:
                print(">= 120 and an < 150" )

                #stopEverything()
                vibrateRoses(0)
                vibrateDogPoos()
                workPump(an+20,DURATION_PUMP, FREQ, an)
                #moveByGroupType(CRUCIFIXES, 2)
            finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 150 and an < 180:
            if DEBUG_MODE:
                print(" 1500 - 180 " )
            if  di < VERY_CLOSE:
                vibrateRoses(0)
                vibrateCrucifixes(5)
            elif  di < CLOSE  and  di > VERY_CLOSE:
                vibrateCrucifixes(5)
            elif  di < VERY_NEAR  and  di > CLOSE:
                print("an >= 150 and an < 180" )
            elif di < OK:
                print("an >= 150 and an < 180" )
            elif  di < FAR  and  di > OK:
                print("an >= 150 and an < 180" )
            elif  di < VERY_FAR  and  di > FAR:
                print("an >= 150 and an < 180" )
                #workPump(0,DURATION_PUMP, FREQ, an)
                finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 180 and an < 210:
            if DEBUG_MODE:
                print(" 180 - 210 " )
            if  di < VERY_CLOSE:
                stopEverything()
                workPump(an+20,DURATION_PUMP, FREQ, an)
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print(">= 180 and an < 210" )
            elif  di < VERY_NEAR  and  di > CLOSE:
                print(">= 180 and an < 210" )
            elif di < OK:
                print(">= 180 and an < 210" )
            elif  di < FAR  and  di > OK:
                print(">= 180 and an < 210" )
            elif  di < VERY_FAR  and  di > FAR:
                #stopEverything()
                vibrateBulb(3)
                stopOne(PUMP_WIRE_NO)
                finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 210 and an < 240:
            if DEBUG_MODE:
                print(" 210 - 240 " )
            if  di < VERY_CLOSE:
                workPump(an+20,DURATION_PUMP, FREQ, an)
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print("an >= 210 and an < 240" )
            elif  di < VERY_NEAR  and  di > CLOSE:
                print("an >= 210 and an < 240" )
            elif di < OK:
                print("an >= 210 and an < 240" )
            elif  di < FAR  and  di > OK:
                print("an >= 210 and an < 240" )
            elif  di < VERY_FAR  and  di > FAR:
                doNorthWest()
                workPump(an+20,DURATION_PUMP, FREQ, an)
                finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 240 and an < 270:
            if  di < VERY_CLOSE:
                workPump(an+20,DURATION_PUMP, FREQ, an)
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print("an >= 240 and an < 270" )
            elif  di < VERY_NEAR  and  di > CLOSE:
                print("an >= 240 and an < 270" )
            elif di < OK:
                print("an >= 240 and an < 270" )
            elif  di < FAR  and  di > OK:
                print("an >= 240 and an < 270" )
            elif  di < VERY_FAR  and  di > FAR:

                stopContinuousServos()
                doNorthEast()
                stopOne(PUMP_WIRE_NO)
                finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 270 and an < 300:
            if  di < VERY_CLOSE:
                workPump(an+20,DURATION_PUMP, FREQ, an)
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print("an >= 270 and an < 300" )
            elif  di < VERY_NEAR  and  di > CLOSE:
                print("an >= 270 and an < 300" )
            elif di < OK:
                print("an >= 270 and an < 300" )
            elif  di < FAR  and  di > OK:
                print("an >= 270 and an < 300" )
            elif  di < VERY_FAR  and  di > FAR:
                stopEverything()
                doSouthEast()
                stopOne(PUMP_WIRE_NO)
                #workPump(di+2000, DURATION_PUMP, FREQ,INTENSITY)
                #time.sleep(26)
                finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 300 and an < 330:
            if DEBUG_MODE:
                print(" 300 - 330 " )
            if  di < VERY_CLOSE:
                print("an >= 300 and an < 330" )
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print("an >= 300 and an < 330" )
            elif  di < VERY_NEAR  and  di > CLOSE:
                print("an >= 300 and an < 330" )
            elif di < OK:
                print("an >= 300 and an < 330" )
            elif  di < FAR  and  di > OK:
                print("an >= 300 and an < 330" )
            elif  di < VERY_FAR  and  di > FAR:
                stopContinuousServos()
                doSouthWest()
                stopOne(PUMP_WIRE_NO)
            #workPump(di+200,DURATION_PUMP, FREQ,INTENSITY)
            #time.sleep(20)
            finishedRoutineCleanUp()
            
        elif di < DISTANCE_MAX_SENSED and an >= 330 and an < 360:
            if DEBUG_MODE:
                print("30 - 360 " )
            if  di < VERY_CLOSE:
                print("an >= 300 and an < 330" )
            elif  di < CLOSE  and  di > VERY_CLOSE:
                print("an >= 300 and an < 330" )
            elif  di < VERY_NEAR  and  di > CLOSE:
                print("an >= 300 and an < 330" )
            elif di < OK:
                print("an >= 300 and an < 330" )
            elif  di < FAR  and  di > OK:
                print("an >= 300 and an < 330" )
            elif  di < VERY_FAR  and  di > FAR:
                stopContinuousServos()
                vibrateRoses(0)
                vibrateCrucifixes(1)
            
                stopOne(PUMP_WIRE_NO)
            finishedRoutineCleanUp()
        
            
    except Exception as e : print(e)
    except SystemExit: 
        os._exit(1)


# This gets angle and distance data generated by the
# RoboPeak Lidar - the data is received here via Open Sound control
# (OSC)
def lidarReceive():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip",
        default=IP, help="The ip to listen on")
        parser.add_argument("--port",
        type=int, default=PORT_NO, help="The port to listen on")
        args = parser.parse_args()

        dispatcher = dispatcher.Dispatcher()
        dispatcher.map("/st", handlerfunction)
        server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
        if DEBUG_MODE:
            print("in lidarReceive... serving on {}".format(server.server_address))
        server.serve_forever()
    except Exception as e: print(e)

def pulseOneServo(num, delayed):

    actuateServoFromNum(num, servo_min)
    time.sleep(delayed)
    actuateServoFromNum(num, servo_max)


'''
pulseEverything used principally as a test routine to
actuate all the servos, motors etc.
'''
def pulseEverything():
    try:
        BUSY = 1
        myMin = servo_min
        myMax = servo_max
        #for i in range(1, 36):
            #print("testing ", i)
            #actuateServoFromNum(i, servo_min)
            #time.sleep(2)
            #actuateServoFromNum(i, servo_max)
        actuateServoFromNum(0, myMin)
        actuateServoFromNum(1, myMin)
        actuateServoFromNum(2, myMin)
        actuateServoFromNum(3, myMin)
        actuateServoFromNum(4, myMin)
        actuateServoFromNum(5, myMin)
        actuateServoFromNum(6, myMin)
        actuateServoFromNum(7, myMin)
        actuateServoFromNum(8, myMin)
        actuateServoFromNum(9, myMin)
        actuateServoFromNum(10, myMin)
        actuateServoFromNum(11, myMin)
        actuateServoFromNum(12, myMin)
        actuateServoFromNum(13, myMin)
        actuateServoFromNum(14, myMin)
        actuateServoFromNum(15, myMin)
        actuateServoFromNum(16, myMin)
        actuateServoFromNum(17, myMin)
        actuateServoFromNum(18, myMin)
        actuateServoFromNum(19, myMin)
        actuateServoFromNum(20, myMin)
        actuateServoFromNum(21, myMin)
        actuateServoFromNum(22, myMin)
        actuateServoFromNum(23, myMin)
        actuateServoFromNum(24, myMin)
        actuateServoFromNum(25, myMin)
        actuateServoFromNum(26, myMin)
        actuateServoFromNum(27, myMin)
        actuateServoFromNum(28, myMin)
        actuateServoFromNum(29, myMin)
        actuateServoFromNum(30, myMin)
        actuateServoFromNum(31, myMin)
        actuateServoFromNum(32, myMin)
        actuateServoFromNum(33, myMin)
        actuateServoFromNum(34, myMin)
        actuateServoFromNum(35, myMin)
        actuateServoFromNum(36, myMin)
        actuateServoFromNum(37, myMin)
        actuateServoFromNum(38, myMin)
        actuateServoFromNum(39, myMin)
        time.sleep(2)
        actuateServoFromNum(0, myMax)
        actuateServoFromNum(1, myMax)
        actuateServoFromNum(2, myMax)
        actuateServoFromNum(3, myMax)
        actuateServoFromNum(4, myMax)
        actuateServoFromNum(5, myMax)
        actuateServoFromNum(6, myMax)
        actuateServoFromNum(7, myMax)
        actuateServoFromNum(8, myMax)
        actuateServoFromNum(9, myMax)
        actuateServoFromNum(10, myMax)
        actuateServoFromNum(11, myMax)
        actuateServoFromNum(12, myMax)
        actuateServoFromNum(13, myMax)
        actuateServoFromNum(14, myMax)
        actuateServoFromNum(15, myMax)
        actuateServoFromNum(16, myMax)
        actuateServoFromNum(17, myMax)
        actuateServoFromNum(18, myMax)
        actuateServoFromNum(19, myMax)
        actuateServoFromNum(20, myMax)
        actuateServoFromNum(21, myMax)
        actuateServoFromNum(22, myMax)
        actuateServoFromNum(23, myMax)
        actuateServoFromNum(24, myMax)
        actuateServoFromNum(25, myMax)
        actuateServoFromNum(26, myMax)
        actuateServoFromNum(27, myMax)
        actuateServoFromNum(28, myMax)
        actuateServoFromNum(29, myMax)
        actuateServoFromNum(30, myMax)
        actuateServoFromNum(31, myMax)
        actuateServoFromNum(32, myMax)
        actuateServoFromNum(33, myMax)
        actuateServoFromNum(34, myMax)
        actuateServoFromNum(35, myMax)
        actuateServoFromNum(36, myMax)
        actuateServoFromNum(37, myMax)
        actuateServoFromNum(38, myMax)
        actuateServoFromNum(39, myMax)
            
        #for i in range(0 ,0):
        #	actuateServoFromNum(i, servo_max)
        #	print("reversing ", i)
        BUSY = 0
        '''
        stopEverything shuts off all devices, called when the program sends
        '''
    except Exception as e: print(e)
    
def stopEverythingWithDisplay():
    try:
        print("stoppping")
        for i in range(1,36):
            actuateServoFromNum(i, 0)
            time.sleep(0.3)
            if DEBUG_MODE:
                print("stopping ",i)
    except Exception as e: print(e)

def stopEverything():
    try:
        BUSY = 1
        for i in range(1,36):
            actuateServoFromNum(0, 0)
            actuateServoFromNum(1, 0)
            actuateServoFromNum(2, 0)
            actuateServoFromNum(3, 0)
            actuateServoFromNum(4, 0)
            actuateServoFromNum(5, 0)
            actuateServoFromNum(6, 0)
            actuateServoFromNum(7, 0)
            actuateServoFromNum(8, 0)
            actuateServoFromNum(9, 0)
            actuateServoFromNum(10, 0)
            actuateServoFromNum(11, 0)
            actuateServoFromNum(12, 0)
            actuateServoFromNum(13, 0)
            actuateServoFromNum(14, 0)
            actuateServoFromNum(15, 0)
            actuateServoFromNum(16, 0)
            actuateServoFromNum(17, 0)
            actuateServoFromNum(18, 0)
            actuateServoFromNum(19, 0)
            actuateServoFromNum(20, 0)
            actuateServoFromNum(21, 0)
            actuateServoFromNum(22, 0)
            actuateServoFromNum(23, 0)
            actuateServoFromNum(24, 0)
            actuateServoFromNum(25, 0)
            actuateServoFromNum(26, 0)
            actuateServoFromNum(27, 0)
            actuateServoFromNum(28, 0)
            actuateServoFromNum(29, 0)
            actuateServoFromNum(30, 0)
            actuateServoFromNum(31, 0)
            actuateServoFromNum(32, 0)
            actuateServoFromNum(33, 0)
            actuateServoFromNum(34, 0)
            actuateServoFromNum(35, 0)
            actuateServoFromNum(36, 0)
            actuateServoFromNum(37, 0)
            actuateServoFromNum(38, 0)
            actuateServoFromNum(39, 0)
            actuateServoFromNum(40, 0)
            actuateServoFromNum(41, 0)
            actuateServoFromNum(42, 0)
            actuateServoFromNum(43, 0)
            actuateServoFromNum(44, 0)
            actuateServoFromNum(45, 0)
            actuateServoFromNum(46, 0)
            actuateServoFromNum(47, 0)
            actuateServoFromNum(48, 0)
            actuateServoFromNum(49, 0)
            actuateServoFromNum(50, 0)
            actuateServoFromNum(51, 0)
            actuateServoFromNum(52, 0)
            actuateServoFromNum(53, 0)
            actuateServoFromNum(54, 0)
            actuateServoFromNum(55, 0)
            actuateServoFromNum(56, 0)
            actuateServoFromNum(57, 0)
            actuateServoFromNum(58, 0)
            actuateServoFromNum(59, 0)
            actuateServoFromNum(60, 0)
            actuateServoFromNum(61, 0)
            actuateServoFromNum(62, 0)
            actuateServoFromNum(63, 0)
            actuateServoFromNum(64, 0)
            actuateServoFromNum(65, 0)
            actuateServoFromNum(66, 0)
            actuateServoFromNum(67, 0)
            actuateServoFromNum(68, 0)
            actuateServoFromNum(69, 0)
            actuateServoFromNum(70, 0)
            actuateServoFromNum(71, 0)
            actuateServoFromNum(72, 0)
            actuateServoFromNum(73, 0)
            actuateServoFromNum(74, 0)
            actuateServoFromNum(75, 0)
            actuateServoFromNum(76, 0)
            actuateServoFromNum(77, 0)
            actuateServoFromNum(78, 0)
            actuateServoFromNum(79, 0)
            actuateServoFromNum(80, 0)

    #		#stopOne(num)
            time.sleep(0)
            stopContinuousServos()
            BUSY = 0
    except Exception as e: print(e)
    
def stopOne(num):
    try:
        
        if DEBUG_MODE:
            print ("in stopOne; stopping ", num)
        BUSY = 1
        actuateServoFromNum(num, 0)
        time.sleep(0)
        BUSY = 0
    except Exception as e: print(e)
    

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    try:
        
        pulse_length = 1000000    # 1,000,000 us per second
        pulse_length //= 60       # 60 Hz
        
        print('{0}us per period'.format(pulse_length))
        pulse_length //= 4096     # 12 bits of resolution
        print('{0}us per bit'.format(pulse_length))
        pulse *= 1000
        pulse //= pulse_length
        pwm1.set_pwm(channel, 0, pulse)
        pwm2.set_pwm(channel, 0, pulse)
        pwm3.set_pwm(channel, 0, pulse)
        pwm4.set_pwm(channel, 0, pulse)
        pwm5.set_pwm(channel, 0, pulse)
        pwm6.set_pwm(channel, 0, pulse)
    except Exception as e: print(e)     
    '''
    ANEMONES=([11,16,18,26,30])
    BANDAGES=([20,24])
    BOXES=([6,7,9,22,31,35])
    BULB=([1,4])
    CRUCIFIXES=([3,10,12,13,21,28,29])
    DOGPOOS=([23,25,32,5])
    ROSES=([0,2,8,14,15,17,19,27,33,34])
    '''


def vibrateAnemones(sleepdelay=0.1, runfor=DEFAULT_RUNNING_TIME):
    try:
        while runfor > 0:
            actuateServoFromNum(11, servo_max)
            actuateServoFromNum(16, servo_max)
            actuateServoFromNum(18, servo_max)
            actuateServoFromNum(26, servo_max)
            actuateServoFromNum(30, servo_max)
            time.sleep(sleepdelay)
            actuateServoFromNum(11, servo_min)
            actuateServoFromNum(16, servo_min)
            actuateServoFromNum(18, servo_min)
            actuateServoFromNum(26, servo_min)
            actuateServoFromNum(30, servo_min)
            time.sleep(sleepdelay)
            runfor=runfor-1;
    except Exception as e: print(e)
    
def vibrateDogPoos(sleepdelay=0.1, runfor=DEFAULT_RUNNING_TIME):
    try:
        while runfor > 0:
            actuateServoFromNum(23, servo_max)
            actuateServoFromNum(25, servo_max)
            actuateServoFromNum(32, servo_max)
            actuateServoFromNum(5, servo_max)
            time.sleep(sleepdelay)
            actuateServoFromNum(23, servo_min)
            actuateServoFromNum(25, servo_min)
            actuateServoFromNum(32, servo_min)
            actuateServoFromNum(5, servo_min)
            time.sleep(sleepdelay)
            runfor=runfor-1;
    except Exception as e: print(e)
    
def vibrateBoxes(sleepdelay=0.1, runfor=DEFAULT_RUNNING_TIME):
    try:
        while runfor > 0:
            actuateServoFromNum(6, servo_max)
            actuateServoFromNum(7, servo_max)
            actuateServoFromNum(9, servo_max)
            actuateServoFromNum(22, servo_max)
            actuateServoFromNum(31, servo_max)
            actuateServoFromNum(35, servo_max)
            time.sleep(sleepdelay)
            actuateServoFromNum(6, servo_min)
            actuateServoFromNum(7, servo_min)
            actuateServoFromNum(9, servo_min)
            actuateServoFromNum(22, servo_min)
            actuateServoFromNum(31, servo_min)
            actuateServoFromNum(35, servo_min)
            time.sleep(sleepdelay)
            runfor=runfor-1;
    except Exception as e: print(e)
    
def vibrateBulb(sleepdelay=0.1, runfor=DEFAULT_RUNNING_TIME):
    try:
        while runfor > 0:
            actuateServoFromNum(1, servo_max)
            actuateServoFromNum(4, servo_max)
            time.sleep(sleepdelay)
            actuateServoFromNum(1, servo_min)
            actuateServoFromNum(4, servo_min)
            time.sleep(sleepdelay)
            runfor=runfor-1;
    except Exception as e: print(e)
    
def vibrateCrucifixes(sleepdelay=0.1, runfor=DEFAULT_RUNNING_TIME):
    try:
        while runfor > 0:
            actuateServoFromNum(3, servo_max)   
            actuateServoFromNum(10, servo_max)
            actuateServoFromNum(12, servo_max)
            actuateServoFromNum(13, servo_max)
            actuateServoFromNum(21, servo_max)
            actuateServoFromNum(28, servo_max)
            actuateServoFromNum(29, servo_max)
            time.sleep(sleepdelay)
            actuateServoFromNum(3, servo_min)
            actuateServoFromNum(10, servo_min)
            actuateServoFromNum(12, servo_min)
            actuateServoFromNum(13, servo_min)
            actuateServoFromNum(21, servo_min)
            actuateServoFromNum(22, servo_min)
            actuateServoFromNum(28, servo_min)
            time.sleep(sleepdelay)
            runfor=runfor-1;
    except Exception as e: print(e)

def vibrateRoses(sleepdelay=0.1, runfor=DEFAULT_RUNNING_TIME):
    try:
        
        while runfor > 0:
            actuateServoFromNum(0, servo_max)
            actuateServoFromNum(2, servo_max)
            actuateServoFromNum(8, servo_max)
            actuateServoFromNum(14, servo_max)
            actuateServoFromNum(15, servo_max)
            actuateServoFromNum(17, servo_max)
            actuateServoFromNum(19, servo_max)
            actuateServoFromNum(27, servo_max)
            actuateServoFromNum(33, servo_max)
            actuateServoFromNum(34, servo_max)
            time.sleep(sleepdelay)	
            actuateServoFromNum(0, servo_min)
            actuateServoFromNum(2, servo_min)
            actuateServoFromNum(8, servo_min)
            actuateServoFromNum(14, servo_min)
            actuateServoFromNum(15, servo_min)
            actuateServoFromNum(17, servo_min)
            actuateServoFromNum(19, servo_min)
            actuateServoFromNum(27, servo_min)
            actuateServoFromNum(33, servo_min)
            actuateServoFromNum(34, servo_max)
            time.sleep(sleepdelay)
            runfor=runfor-1;
    except Exception as e: print(e)
    
    
def CrucifixesThenRoses():
    try:
        #vibrateCrucifixes()
        time.sleep(3)
        vibrateRoses()
    except Exception as e: print(e)
        
def doNorthWest(runfor=DEFAULT_RUNNING_TIME):
    try:
        while runfor > 0:
            actuateServoFromNum(5, servo_max)
            actuateServoFromNum(6, servo_max)
            actuateServoFromNum(12, servo_max)
            actuateServoFromNum(15, servo_max)
            actuateServoFromNum(22, servo_max)
            actuateServoFromNum(27, servo_max)
            actuateServoFromNum(21, servo_max)
            actuateServoFromNum(26, servo_max)
            actuateServoFromNum(4, servo_max)
            time.sleep(0.1)	
            actuateServoFromNum(5, servo_min)
            actuateServoFromNum(6, servo_min)
            actuateServoFromNum(12, servo_min)
            actuateServoFromNum(15, servo_min)
            actuateServoFromNum(22, servo_min)
            actuateServoFromNum(27, servo_min)
            actuateServoFromNum(21, servo_min)
            actuateServoFromNum(26, servo_min)
            actuateServoFromNum(4, servo_min)
            runfor=runfor-1;
    except Exception as e: print(e)
    
def doNorthEast(runfor=DEFAULT_RUNNING_TIME):
#NE=([7,17,23,9])
    try:
        while runfor > 0:
            actuateServoFromNum(7, servo_max)
            actuateServoFromNum(17, servo_max)
            actuateServoFromNum(23, servo_max)
            actuateServoFromNum(9, servo_max)
            time.sleep(0.1)	
            actuateServoFromNum(7, servo_min)
            actuateServoFromNum(17, servo_min)
            actuateServoFromNum(23, servo_min)
            actuateServoFromNum(9, servo_min)
            runfor=runfor-1;
    except Exception as e: print(e)
    
def doSouthEast(runfor=DEFAULT_RUNNING_TIME):
#SE=([34,18,13,1,29,32,20,19,9,2])
    try:
        while runfor > 0:
            actuateServoFromNum(34, servo_max)
            actuateServoFromNum(18, servo_max)
            actuateServoFromNum(13, servo_max)
            actuateServoFromNum(1, servo_max)
            actuateServoFromNum(29, servo_max)
            actuateServoFromNum(32, servo_max)
            actuateServoFromNum(20, servo_max)
            actuateServoFromNum(19, servo_max)
            actuateServoFromNum(9, servo_max)
            actuateServoFromNum(2, servo_max)
            time.sleep(0.1)
            actuateServoFromNum(34, servo_min)
            actuateServoFromNum(18, servo_min)
            actuateServoFromNum(13, servo_min)
            actuateServoFromNum(1, servo_min)
            actuateServoFromNum(29, servo_min)
            actuateServoFromNum(32, servo_min)
            actuateServoFromNum(20, servo_min)
            actuateServoFromNum(19, servo_min)
            actuateServoFromNum(9, servo_min)
            actuateServoFromNum(2, servo_min)
            runfor=runfor-1;
    except Exception as e: print(e)
    
def doSouthWest(runfor=DEFAULT_RUNNING_TIME):
#SW=([11,20,31,3,14,25,36,10])
    try:
        while runfor > 0:
            actuateServoFromNum(11, servo_max)
            actuateServoFromNum(20, servo_max)
            actuateServoFromNum(31, servo_max)
            actuateServoFromNum(3, servo_max)
            actuateServoFromNum(14, servo_max)
            actuateServoFromNum(25, servo_max)
            actuateServoFromNum(36, servo_max)
            actuateServoFromNum(10, servo_max)
            time.sleep(0.1)
            actuateServoFromNum(11, servo_min)
            actuateServoFromNum(20, servo_min)
            actuateServoFromNum(31, servo_min)
            actuateServoFromNum(3, servo_min)
            actuateServoFromNum(14, servo_min)
            actuateServoFromNum(25, servo_min)
            actuateServoFromNum(36, servo_min)
            actuateServoFromNum(10, servo_min)
            actuateServoFromNum(19, servo_min)
            runfor=runfor-1;
    except Exception as e: print(e)
    
def periodicPumpAction(runfor=DEFAULT_RUNNING_TIME):
    try:
        while runfor > 0:
            for i in range (1000, 2000,250): 
                workPump(i,2.2,1,1000)
                if i == 1000:
                    workPump(0,2.2,1,1000)
                    time.sleep(2)
                    workPump(1,2.2,1,1000)
            runfor=runfor-1;
    except Exception as e: print(e)
    
# Todo:
# ===============
# Spirals around bin?
# down to up
# up to down
# slow mode
# what if no one is there?


#def main():
#now = time.time()

#while True:
	#diff = now- then
	#print (now)
	#print (then)
	#time.sleep(1)
#while int(diff%60)== 0:
	#print ("NOTHING SEEN")
def attractAttentionGuys():
    try:
        ATTRACTIONMODE=1
        for i in range (1000, 2000,250): 
                workPump(i,2.2,1,1000)
                
                if i == 1000:
                    workPump(0,2.2,1,1000)
                    time.sleep(2)
                    workPump(1,2.2,1,1000)
        ATTRACTIONMODE=0
    except Exception as e: print(e)
    
def testx(num):
    try:
        pwm2.set_pwm(num, 0, 170)

        if DEBUG_MODE:
            print('0 degrees')
        time.sleep(2)
        pwm2.set_pwm(num, 0, 252)
        if DEBUG_MODE:
            print('45 degrees')
        time.sleep(2)
        if DEBUG_MODE:
            print('90 degrees')
        pwm2.set_pwm(num, 0, 376)
        time.sleep(2)
        pwm2.set_pwm(num, 0, 500)
        if DEBUG_MODE:
            print('125 degrees')
        time.sleep(2)
        pwm2.set_pwm(num, 0, 585)
        if DEBUG_MODE:
            print('180 degrees')
        time.sleep(2)
    except Exception as e: print(e)
    
def timer():
    try:
        TIME_INTERVAL = 2
        while True:
            # wake up and test every TIME_INTERVAL
            time.sleep(TIME_INTERVAL)
            if BUSY == 0:
                # its here that we can call our 'attention-getting routine
                # to entice the punters to come over and have a look
                attractAttentionGuys()
                print("in background thread timer, no-one around")
        for j in threads:
            if not j.isAlive():
                threads.remove(j)
        for j in threads:
            j.join()
    except Exception as e: print(e)
    

background_thread = Thread(target=timer, args=())
background_thread.start()

try:
    if LIDAR_RECEIVE:
        #
        # pick up the OSC messages coming in
        #
        #dieat = time.time()
        #print(dieat)
        #print ("**** " , int(dieat)+5.0 - int(time.time()))
    
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip",
          default=IP, help="The ip to listen on")
        parser.add_argument("--port",
          type=int, default=PORT_NO, help="The port to listen on")
        args = parser.parse_args()

        dispatcher = dispatcher.Dispatcher()
        dispatcher.map("/st", handlerfunction)


        server = osc_server.ThreadingOSCUDPServer(
          (args.ip, args.port), dispatcher)
        

        if DEBUG_MODE:
            print("Serving on {}".format(server.server_address))
        server.serve_forever()
        
    else:

        '''
        #device_types:
        ANEMONE=1
        BANDAGE=2
        BOX=3
        BULB=4
        CRUCIFIX=5
        DOGPOO=6
        ROSE=7
        IS_NW=8
        IS_SE=9
        IS_SW=10
        CONTINOUS=11
        '''
        #stopEverything()

        # No Lidar here. Used in testing...
        #for i in range (1, 7):
            #choregraphyActioByTypeOfObject(i, 0.1, servo_min)
            #time.sleep(1)
            #choregraphyActioByTypeOfObject(i, 0.1, servo_max)
        #stopEverything()
        
        #choregraphyActioByTypeOfObject(1, 2, servo_min)
        #num =  48
        #print(num)
        #pwm4.set_pwm_freq(60)
        while True:
            testx(31)
            ##power, duration, freq, intensity
            #for i in range (1000, 2000,250): 
                #workPump(i,2.2,1,1000)
                
                #if i == 1000:
                    #workPump(0,2.2,1,1000)
                    #time.sleep(2)
                    #workPump(1,2.2,1,1000)
            #vibrateDogPoos(1)    
            #vibrateRoses(1)
            #vibrateCrucifixes(0.2)
            #actuateServoFromNum(47, 170)
            #time.sleep(2)
            #actuateServoFromNum(47, 550)
            #time.sleep(2)
            #actuateServoFromNum(64, 600)
            #time.sleep(2)
            #actuateServoFromNum(64, 0)
            #time.sleep(2)
            #pulseEverything()
            #pwm3.set_pwm(15, 0, 175)
            #time.sleep(2)
            #pwm3.set_pwm(15, 0, 550)
            #time.sleep(2)
		##	doNorthEast()
		#	doSouthWest()
		#	doSouthEast()
			#stopContinuousServos()
            
            #pulseEverything()
		#while True:
			#pulseOneServo(1, 1.5)
			#stopOne(46)
			#stopEverything()


        #stopEverythingWithDisplay()


except KeyboardInterrupt:
        stopEverything()
        print("Ctl C pressed - ending program")
#except Exception: 
#    os._exit(1)

#if __name__ == '__main__':
#	main()



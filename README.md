This code is for two Raspberry Pi's
1. running the code to receive the lidar sensor and forward the readings via OSC to the secon Pi.
2. the second Pi runs a processing sketch which receives the OSC lidar data and throttles it and displays
the polar coordinates as Cartesian coordinates. The throttled readings are forwarded to a display_servos.py program which controls the pump and servos using Adafruit I2C boards connected in series. 
# forgiveness_machine
# forgiveness_machine

# lidar_servos
The processingf sketch processingReceiveTestb.pde is started and this sends lidar position data via OSC to
the python script run_display_servos_fix.py. This python script will soon run out of threads - so as a workaround I have the startExhibit.sh and startExhibit.py program to create both the pde and py and then every few secods (3?) it kills the py program and restarts it again. The processing sketch remains running until it is all killed off with another script stopExhibit.py

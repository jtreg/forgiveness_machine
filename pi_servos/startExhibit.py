#  this script starts display_servos.py and kills it,
# restarts it so that the python script can
# overcome the problem in the library module'{# memory leak

import os
import subprocess
import time


print('launching processing')
#subprocess.Popen("/home/pi/python/osc/processingReceiveTestb/application.linux-arm64/processingReceiveTestb", close_fds=True)

print('launching servos python script')
subprocess.Popen("./run_display_servos_fix.sh", close_fds=True)

    process_id = ""

# read process id
with open("~/python/osc/displayservosPID", "r") as f:
    process_id = f.read()

print(process_id)

#time.sleep(5)


print('end of program')

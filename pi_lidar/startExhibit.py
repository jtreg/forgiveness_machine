import os
import subprocess
import time

#command="/home/pi/python/osc/processingReceiveTest/application.linux-arm64/processingReceiveTest"
#command_servos = "python3 ~/python/osc/display_servos.py &"
# launch processing
#os.spawnl(os.P_DETACH, "/home/pi/python/osc/processingReceiveTest/application.linux-arm64/processingReceiveTest")
#os.spawn(os.P_DETACH, "python3 ~/python/osc/display_servos.py &")
#os.spawnl(os.P_NOWAIT, *command)
#os.spawnl(os.P_NOWAIT, *command_servos)


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

# kill the process
#os.spawn(os.P_DETACH, "kill -9 ${}".format(process_id))

print('end of program')

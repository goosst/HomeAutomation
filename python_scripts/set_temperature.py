import subprocess
import time
import getopt
import sys
#from ilock import ILock

# check if passed options are valid
try:
    options, args = getopt.getopt(sys.argv[1:], 't:',['temperature_setpoint='])
    print(options)
    print(args)
except getopt.GetoptError:
    print("incorrect syntax")
    print("usage: python3 set_temperature.py -t <value>")
    print("default to 12 degrees")
    msg2=12
    sys.exit(2)
for opt, value in options:
    if opt in ('-t','-T','--temperature_setpoint'):
        msg2=value
        print("successful argument")
        print(msg2)

#with ILock('ebus', timeout=200):
msg1="ebusctl write -c f37 Hc1DayTemp "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

msg1="ebusctl write -c f37 Hc1NightTemp "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

time.sleep(30)

#check if it is truly set
cp = subprocess.run(["ebusctl read Hc1DayTemp"],shell=True,stdout=subprocess.PIPE)
temp=cp.stdout
if int(float(temp[0:4]))!=int(float(msg2)):
    # if not set correct
    msg1="ebusctl write -c f37 Hc1DayTemp "
    cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

cp = subprocess.run(["ebusctl read Hc1NightTemp"],shell=True,stdout=subprocess.PIPE)
temp=cp.stdout
if int(float(temp[0:4]))!=int(float(msg2)):
    # if not set correct
    msg1="ebusctl write -c f37 Hc1NightTemp "
    cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
else:
    print("setting correct")

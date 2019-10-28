import subprocess
import time
import getopt
import sys
from ilock import ILock

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

numberOfIterationsMax=5

with ILock('ebus', timeout=200):
    msg1="ebusctl write -c f37 Hc1DayTemp "
    cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

    msg1="ebusctl write -c f37 Hc1NightTemp "
    cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
    time.sleep(30)
    correctSetting=False
    cntr1=0
    while (correctSetting == False) and (cntr1<numberOfIterationsMax):
        # get Hc1DayTemp reading
        cntr=0
        busread='ERR'
        while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
            cp = subprocess.run(["ebusctl read Hc1DayTemp"],shell=True,stdout=subprocess.PIPE)
            cp_string=cp.stdout.decode('utf-8')
            busread=cp_string[0:5]
            print(busread)
            time.sleep(5)
            cntr=cntr+1
            print(cntr)

        #check if it is truly set
        temp=cp.stdout
        if int(float(temp[0:4]))!=int(float(msg2)):
            # if not set correct, try to set it again
            msg1="ebusctl write -c f37 Hc1DayTemp "
            cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
        else:
            correctSetting=True
            print('setting Hc1DayTemp matches')
            print(correctSetting)
        cntr1=cntr1+1
        time.sleep(15)

    correctSetting=False
    cntr1=0
    while (correctSetting == False) and (cntr1<numberOfIterationsMax):
        # get Hc1DayTemp reading
        cntr=0
        busread='ERR'
        while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
            cp = subprocess.run(["ebusctl read Hc1NightTemp"],shell=True,stdout=subprocess.PIPE)
            cp_string=cp.stdout.decode('utf-8')
            busread=cp_string[0:5]
            print(busread)
            time.sleep(5)
            cntr=cntr+1
            print(cntr)

        #check if it is truly set
        temp=cp.stdout
        if int(float(temp[0:4]))!=int(float(msg2)):
            # if not set correct, try to set it again
            msg1="ebusctl write -c f37 Hc1NightTemp "
            cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
        else:
            correctSetting=True
            print('setting Hc1NightTemp matches')
        cntr1=cntr1+1
        time.sleep(15)
	# cp = subprocess.run(["ebusctl read Hc1NightTemp"],shell=True,stdout=subprocess.PIPE)
	# temp=cp.stdout
	# if int(float(temp[0:4]))!=int(float(msg2)):
	#     # if not set correct
	#     msg1="ebusctl write -c f37 Hc1NightTemp "
	#     cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
	# else:
	#     print("setting correct")

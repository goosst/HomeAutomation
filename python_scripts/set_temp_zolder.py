import subprocess
import time
import getopt
import sys
from ilock import ILock
import logging
import os

cwd = os.getcwd()
path="/home/homeassistant/.homeassistant/www"
os.chdir(path)

logging.basicConfig(filename='debug_set_temp_zolder',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

logging.debug("start directory")
logging.debug(cwd)

# check if passed options are valid
try:
    options, args = getopt.getopt(sys.argv[1:], 't:',['temperature_setpoint='])
    logging.debug(options)
    logging.debug(args)
except getopt.GetoptError:
    logging.debug("incorrect syntax")
    logging.debug("usage: python3 set_temperature.py -t <value>")
    logging.debug("default to 7 degrees")
    msg2=7
    sys.exit(2)
for opt, value in options:
    if opt in ('-t','-T','--temperature_setpoint'):
        msg2=value
        logging.debug("successful argument")
        logging.debug(msg2)

numberOfIterationsMax=5

msg1="ebusctl write -c b7v z2DayTemp "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
time.sleep(1)

msg1="ebusctl write -c b7v z2NightTemp "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
time.sleep(1)

msg1="ebusctl write -c b7v z2ActualRoomTempDesired "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
time.sleep(5)

correctSetting=False
cntr1=0
while (correctSetting == False) and (cntr1<numberOfIterationsMax):
    # get Hc1DayTemp reading
    cntr=0
    busread='ERR'
    while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
        cp = subprocess.run(["ebusctl read z2DayTemp"],shell=True,stdout=subprocess.PIPE)
        cp_string=cp.stdout.decode('utf-8')
        busread=cp_string[0:5]
        logging.debug("z2daytemp")
        logging.debug(busread)
        time.sleep(5)
        cntr=cntr+1
        logging.debug(cntr)

    #check if it is truly set
    temp=cp.stdout
    if int(float(temp[0:4]))!=int(float(msg2)):
        # if not set correct, try to set it again
        msg1="ebusctl write -c b7v z2DayTemp "
        cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
        time.sleep(15)
    else:
        correctSetting=True
        logging.debug('setting z2DayTemp matches')
        logging.debug(correctSetting)
    cntr1=cntr1+1

correctSetting=False
cntr1=0
while (correctSetting == False) and (cntr1<numberOfIterationsMax):
    # get Hc1DayTemp reading
    cntr=0
    busread='ERR'
    while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
        cp = subprocess.run(["ebusctl read z2NightTemp"],shell=True,stdout=subprocess.PIPE)
        cp_string=cp.stdout.decode('utf-8')
        busread=cp_string[0:5]
        logging.debug("z2NightTemp")
        logging.debug(busread)
        time.sleep(5)
        cntr=cntr+1
        logging.debug(cntr)

    #check if it is truly set
    temp=cp.stdout
    if int(float(temp[0:4]))!=int(float(msg2)):
        # if not set correct, try to set it again
        msg1="ebusctl write -c b7v z2NightTemp "
        cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
        time.sleep(15)
    else:
        correctSetting=True
        logging.debug('setting z2NightTemp matches')
    cntr1=cntr1+1

cp = subprocess.run(["ebusctl read z2ActualRoomTempDesired"],shell=True,stdout=subprocess.PIPE)
cp_string=cp.stdout.decode('utf-8')
busread=cp_string[0:5]
logging.debug("z2ActualRoomTempDesired")
logging.debug(busread)
time.sleep(5)
temp=cp.stdout
if int(float(temp[0:4]))!=int(float(msg2)):
    logging.debug('setting z2ActualRoomTempDesired matches msg2')



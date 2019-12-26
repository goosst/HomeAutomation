import subprocess
import time
from ilock import ILock
import logging
import os

numberOfIterationsMax=5
cwd = os.getcwd()

path="/home/homeassistant/.homeassistant/www"
os.chdir(path)

logging.basicConfig(filename='debug_ebus',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.ERROR)

logging.debug("start directory")
logging.debug(cwd)
# with ILock('ebus', timeout=200):
#read temperature measured by thermostat
#time.sleep(3)
logging.debug("read ebus started")
cp = subprocess.run(["ebusctl read RoomTemp"],shell=True,stdout=subprocess.PIPE)
logging.debug("read RoomTemp 1")
logging.debug(cp)
cp_string=cp.stdout.decode('utf-8')
busread=cp_string[0:5]
if busread == 'error':
	# cp = subprocess.run(["ebusd -f --scanconfig >/dev/null 2>&1"],shell=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.Popen(["nohup", "ebusd", "-f", "--scanconfig"])
	print('fubar')
	time.sleep(60)
	cp = subprocess.run(["ebusctl read RoomTemp"],shell=True,stdout=subprocess.PIPE)
	logging.error("read RoomTemp 2")
	logging.error(cp)
	cp_string=cp.stdout.decode('utf-8')
	busread=cp_string[0:5]
time.sleep(1)
cntr=0
while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
	cp = subprocess.run(["ebusctl read RoomTemp"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	busread=cp_string[0:5]
	time.sleep(5)
	logging.error("counter:")
	logging.error(cntr)
	logging.error(busread)
	cntr=cntr+1
msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature -u stijn -P mqtt -m "
cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
logging.debug("send mqtt RoomTemp")
logging.debug(busread)
logging.debug(cp)
time.sleep(3)




# read temperature setpoint
logging.debug("read DisplayedHc1RoomTempDesired")
cp = subprocess.run(["ebusctl read DisplayedHc1RoomTempDesired"],shell=True,stdout=subprocess.PIPE)
cp_string=cp.stdout.decode('utf-8')
#print(cp_string)
busread=cp_string[0:4]
#print(busread)
# if busread == 'erro':
# 	#try again
# 	logging.error("DisplayedHc1RoomTempDesired could not be read")
# 	time.sleep(2)
# 	cp = subprocess.run(["ebusctl read DisplayedHc1RoomTempDesired"],shell=True,stdout=subprocess.PIPE)
# 	cp_string=cp.stdout.decode('utf-8')
# 	busread=cp_string[0:4]
cntr=0
while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
	cp = subprocess.run(["ebusctl read DisplayedHc1RoomTempDesired"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	busread=cp_string[0:5]
	time.sleep(5)
	logging.debug("counter:")
	logging.debug(cntr)
	logging.debug(busread)
	cntr=cntr+1
msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_set -u stijn -P mqtt -m "
cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
logging.debug("send mqtt DisplayedHc1RoomTempDesired")
logging.debug(busread)
logging.debug(cp)
time.sleep(3)

# read temperature flow heating
cp = subprocess.run(["ebusctl read Hc1ActualFlowTempDesired"],shell=True,stdout=subprocess.PIPE)
cp_string=cp.stdout.decode('utf-8')
#print(cp_string)
busread=cp_string[0:4]
# if busread == 'erro':
# 	#try again
# 	logging.error("Hc1ActualFlowTempDesired could not be read")
# 	time.sleep(2)
# 	cp = subprocess.run(["ebusctl read Hc1ActualFlowTempDesired"],shell=True,stdout=subprocess.PIPE)
# 	cp_string=cp.stdout.decode('utf-8')
# 	busread=cp_string[0:4]
#print(busread)
cntr=0
while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
	cp = subprocess.run(["ebusctl read Hc1ActualFlowTempDesired"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	busread=cp_string[0:5]
	time.sleep(5)
	logging.debug("counter:")
	logging.debug(cntr)
	logging.debug(busread)
	cntr=cntr+1
msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_flowtemp -u stijn -P mqtt -m "
cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)

# read time
#cp = subprocess.run(["ebusctl read Time"],shell=True,stdout=subprocess.PIPE)
#cp_string=cp.stdout.decode('utf-8')
#time_read=cp_string[0:8]
#msg1="mosquitto_pub -h localhost -t sensor/thermostat/fubar -u stijn -P mqtt -m "
#print(time_read)
#cp = subprocess.run([msg1+time_read],shell=True,stdout=subprocess.PIPE)

import subprocess
import time
from ilock import ILock
import logging
import os
# 12 mar 21: adapted to new VR70 with VRC700 (and VR91f)

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
with ILock('ebus', timeout=200):
	#read temperature measured by thermostat
	#time.sleep(3)
	logging.debug("read ebus started")
	cp = subprocess.run(["ebusctl read z1RoomTemp"],shell=True,stdout=subprocess.PIPE)
	logging.debug("read RoomTemp 1")
	logging.debug(cp)
	cp_string=cp.stdout.decode('utf-8')
	busread=cp_string[0:5]
	if busread == 'error':
		# cp = subprocess.run(["ebusd -f --scanconfig >/dev/null 2>&1"],shell=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		subprocess.Popen(["nohup", "ebusd", "-f", "--scanconfig"])
		print('fubar')
		time.sleep(5)
		cp = subprocess.run(["ebusctl read z1RoomTemp"],shell=True,stdout=subprocess.PIPE)
		logging.error("read RoomTemp 2")
		logging.error(cp)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
	time.sleep(1)
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read z1RoomTemp"],shell=True,stdout=subprocess.PIPE)
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
logging.debug("read z1ActualRoomTempDesired")
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read z1ActualRoomTempDesired"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read z1ActualRoomTempDesired"],shell=True,stdout=subprocess.PIPE)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
		time.sleep(5)
		logging.debug("counter:")
		logging.debug(cntr)
		logging.debug(busread)
		cntr=cntr+1
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_set -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	logging.debug("send mqtt z1ActualRoomTempDesired")
	logging.debug(busread)
	logging.debug(cp)
	time.sleep(3)

# read temperature flow heating
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read Hc1ActualFlowTempDesired"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
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


# read actual temperature flow
logging.debug("read Hc1FlowTemp")
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read Hc1FlowTemp"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read Hc1FlowTemp"],shell=True,stdout=subprocess.PIPE)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
		time.sleep(5)
		logging.debug("counter:")
		logging.debug(cntr)
		logging.debug(busread)
		cntr=cntr+1
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_flow -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	logging.debug("send mqtt Hc1FlowTemp")
	logging.debug(busread)
	logging.debug(cp)
	time.sleep(3)



# read time
#cp = subprocess.run(["ebusctl read Time"],shell=True,stdout=subprocess.PIPE)
#cp_string=cp.stdout.decode('utf-8')
#time_read=cp_string[0:8]
#msg1="mosquitto_pub -h localhost -t sensor/thermostat/fubar -u stijn -P mqtt -m "
#print(time_read)
#cp = subprocess.run([msg1+time_read],shell=True,stdout=subprocess.PIPE)

##############################################################################
###############################################################################
# zolder

# read temperature setpoint zolder
logging.debug("read z2ActualRoomTempDesired")
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read z2ActualRoomTempDesired"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read z2ActualRoomTempDesired"],shell=True,stdout=subprocess.PIPE)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
		time.sleep(5)
		logging.debug("counter:")
		logging.debug(cntr)
		logging.debug(busread)
		cntr=cntr+1
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_zolder_set -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	logging.debug("send mqtt z2ActualRoomTempDesired")
	logging.debug(busread)
	logging.debug(cp)
	time.sleep(3)



# read temperature zolder
logging.debug("read z2RoomTemp")
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read z2RoomTemp"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read z2RoomTemp"],shell=True,stdout=subprocess.PIPE)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
		time.sleep(5)
		logging.debug("counter:")
		logging.debug(cntr)
		logging.debug(busread)
		cntr=cntr+1
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_zolder_vaillant -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	logging.debug("send mqtt z2RoomTemp")
	logging.debug(busread)
	logging.debug(cp)
	time.sleep(3)

# read desired flow temperature zolder
logging.debug("read Hc2ActualFlowTempDesired")
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read Hc2ActualFlowTempDesired"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read Hc2ActualFlowTempDesired"],shell=True,stdout=subprocess.PIPE)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
		time.sleep(5)
		logging.debug("counter:")
		logging.debug(cntr)
		logging.debug(busread)
		cntr=cntr+1
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_flowtemp_zolder_set -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	logging.debug("send mqtt Hc2ActualFlowTempDesired")
	logging.debug(busread)
	logging.debug(cp)
	time.sleep(3)

# read actual temperature flow
logging.debug("read Hc2FlowTemp")
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read Hc2FlowTemp"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read Hc2FlowTemp"],shell=True,stdout=subprocess.PIPE)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
		time.sleep(5)
		logging.debug("counter:")
		logging.debug(cntr)
		logging.debug(busread)
		cntr=cntr+1
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_flowtemp_zolder -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	logging.debug("send mqtt Hc2FlowTemp")
	logging.debug(busread)
	logging.debug(cp)
	time.sleep(3)

#######################################################################


# read outside temperature
logging.debug("read DisplayedOutsideTemp")
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read DisplayedOutsideTemp"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read DisplayedOutsideTemp"],shell=True,stdout=subprocess.PIPE)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
		time.sleep(5)
		logging.debug("counter:")
		logging.debug(cntr)
		logging.debug(busread)
		cntr=cntr+1
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_outside_vaillant -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	logging.debug("send mqtt DisplayedOutsideTemp")
	logging.debug(busread)
	logging.debug(cp)
	time.sleep(3)

# read waterpressure
logging.debug("read WaterPressure")
with ILock('ebus', timeout=200):
	cp = subprocess.run(["ebusctl read WaterPressure"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	cntr=0
	while (busread[0:3]=='ERR') and (cntr<numberOfIterationsMax):
		cp = subprocess.run(["ebusctl read WaterPressure"],shell=True,stdout=subprocess.PIPE)
		cp_string=cp.stdout.decode('utf-8')
		busread=cp_string[0:5]
		time.sleep(5)
		logging.debug("counter:")
		logging.debug(cntr)
		logging.debug(busread)
		cntr=cntr+1
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/pressure_vaillant -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	logging.debug("send mqtt WaterPressure")
	logging.debug(busread)
	logging.debug(cp)
	time.sleep(3)
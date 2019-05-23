import subprocess
import time
from ilock import ILock

with ILock('ebus', timeout=200):
	#read temperature measured by thermostat
	time.sleep(3)
	cp = subprocess.run(["ebusctl read RoomTemp"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	busread=cp_string[0:5]
	time.sleep(1)
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	time.sleep(3)

	# read temperature setpoint
	cp = subprocess.run(["ebusctl read DisplayedHc1RoomTempDesired"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	#print(busread)
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_set -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)
	time.sleep(3)

	# read temperature flow heating
	cp = subprocess.run(["ebusctl read Hc1ActualFlowTempDesired"],shell=True,stdout=subprocess.PIPE)
	cp_string=cp.stdout.decode('utf-8')
	#print(cp_string)
	busread=cp_string[0:4]
	#print(busread)
	msg1="mosquitto_pub -h localhost -t sensor/thermostat/temperature_flowtemp -u stijn -P mqtt -m "
	cp = subprocess.run([msg1+busread],shell=True,stdout=subprocess.PIPE)

	# read time
	#cp = subprocess.run(["ebusctl read Time"],shell=True,stdout=subprocess.PIPE)
	#cp_string=cp.stdout.decode('utf-8')
	#time_read=cp_string[0:8]
	#msg1="mosquitto_pub -h localhost -t sensor/thermostat/fubar -u stijn -P mqtt -m "
	#print(time_read)
	#cp = subprocess.run([msg1+time_read],shell=True,stdout=subprocess.PIPE)


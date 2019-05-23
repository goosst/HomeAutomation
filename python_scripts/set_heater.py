import subprocess
import datetime
from ilock import ILock

time_on=datetime.time( 5,30,0 ) # time(hour,minute,second)
time_off=datetime.time( 5,59,0 )

if time_off>time_on:
	offtime_later_ontime=True
else:
	offtime_later_ontime=False

if datetime.datetime.now().time()>time_on and datetime.datetime.now().time()<time_off and offtime_later_ontime:
	msg2="ON"
elif datetime.datetime.now().time()>time_off and offtime_later_ontime:
	msg2="OFF"
else:
	msg2="OFF"

msg1="mosquitto_pub -h localhost -t cmnd/sonoff/Power1 -u stijn -P mqtt -m "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
#print(msg2)

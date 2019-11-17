# turns electric heater on and off from home assistant
# 17 nov 19: differentiates between manually turned on and automatically turned on, to decide when to turn heater off
import subprocess
import datetime
# from ilock import ILock
from requests import get,post
import json
# from datetime import datetime, timedelta
import datetime
from pytz import timezone
import numpy as np

#laptop
headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI3YmNjY2FhNTBlNDM0YjFhOThiMWE4M2Q3ZjU5Zjg5NyIsImlhdCI6MTU3Mjc3NjI0MywiZXhwIjoxODg4MTM2MjQzfQ.tMw-7qFAyqNkGOBXXcg3hqmC1R-HAxf2agZ9d-i3Saw',
    'content-type': 'application/json',
}

#headers = {
#    'Authorization': 'Bearer #eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI3NzYxN2Q4YjM0ODA0MTAwYjgyYWQ1ZmE5NjM0NjU2NiIsImlhdCI6MTU2ODc0NDQwMiwiZXhwIjoxODg0MTA0NDAyfQ.XB6RrMAmHPsnXnjsnOPnMjIs0_hSWq-#visg1NYcXK0w',
#    'content-type': 'application/json',
#}
address_hass='192.168.0.205'
# get timezone to convert to local time, since database attributes are in UTC time
url='http://'+address_hass+':8123/api/config'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)
time_zone=readable_json['time_zone']
tz = timezone(time_zone)

# # get latest time
# url='http://'+address_hass+':8123/api/states/sensor.date_time_iso'
# response = get(url, headers=headers)
# temp=response.text
# readable_json=json.loads(temp)
#
# hass_time_real = datetime.strptime(readable_json['state'], '%Y-%m-%dT%H:%M:%S')
# hass_time_recorder=datetime.strptime(readable_json['last_changed'],'%Y-%m-%dT%H:%M:%S.%f%z')

entity_id='sensor.temperature_bathroom'
url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
response = get(url, headers=headers)
temp=response.text
temp=temp[1:len(temp)-1]
readable_json=json.loads(temp)

time_array= np.array([])
state_array=np.array([])
for i in readable_json:
    try:
        state_array=np.append(state_array,float(i['state']))
        time_update=datetime.datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
        time_array=np.append(time_array, time_update.astimezone(tz))
    except:
        print("unknown state")

# last timestap
time_last=time_array[-1]
temp_last=state_array[-1]

# check status of switch
entity_id='binary_sensor.heater_status'
url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
response = get(url, headers=headers)
temp=response.text
temp=temp[1:len(temp)-1]
readable_json=json.loads(temp)

time_array_switch= np.array([])
state_array_switch=np.array([])
for i in readable_json:
    try:
        state_array_switch=np.append(state_array_switch,i['state'])
        time_update=datetime.datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
        time_array_switch=np.append(time_array_switch, time_update.astimezone(tz))
    except:
        print("unknown state")

# last timestap
time_last_switch=time_array_switch[-1]
state_last_switch=state_array_switch[-1]

# was the heater turned on manually?
entity_id='input_number.dummy_heater'
url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
response = get(url, headers=headers)
temp=response.text
temp=temp[1:len(temp)-1]
readable_json=json.loads(temp)

time_array_dummyheater= np.array([])
state_array_dummyheater=np.array([])
for i in readable_json:
    try:
        state_array_dummyheater=np.append(state_array_dummyheater,i['state'])
        time_update=datetime.datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
        time_array_dummyheater=np.append(time_array_dummyheater, time_update.astimezone(tz))
    except:
        print("unknown state")

# last timestap
time_last_dummyheater=time_array_dummyheater[-1]
state_last_dummyheater=state_array_dummyheater[-1]

if (state_last_dummyheater!='auto_on') and (state_last_switch=='on'):
    manual_heating=True
else:
    manual_heating=False
print(manual_heating)


#turn on heater if temp is too low in the morning
time_on=datetime.time( 5,20,0 )
time_off=datetime.time( 5,59,0 ) #nachttarrief
now=datetime.datetime.now().astimezone(tz)


if time_off>time_on:
	offtime_later_ontime=True
else:
	offtime_later_ontime=False

url='http://'+address_hass+':8123/api/states/input_number.dummy_heater'
if now.time()>time_on and now.time()<time_off and offtime_later_ontime and temp_last<17:
    msg2="ON" # communicate to hass heater was turned on automatically
    payload='{"state": "auto_on"}'
    post(url,data=payload,headers=headers)
elif now.time()>time_off and offtime_later_ontime or temp_last>20:
    msg2="OFF"
    payload='{"state": "auto_off"}'
    post(url,data=payload,headers=headers)
else:
	msg2="OFF"

if manual_heating==False:
    msg1="mosquitto_pub -h localhost -t cmnd/sonoff/Power1 -u stijn -P mqtt -m "
    cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
#print(msg2)

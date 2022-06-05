# turn switch off when power is low over last period of time

import subprocess
import datetime
from requests import get,post
import json
from pytz import timezone
import numpy as np
import pdb

powerthreshold=12 #watt, turn off when below power

# import long-live token
import headerfiles as parameters
headers=parameters.headers
address_hass=parameters.address_hass

# get timezone to convert to local time, since database attributes are in UTC time
url='http://'+address_hass+':8123/api/config'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)
time_zone=readable_json['time_zone']
tz = timezone(time_zone)

# get latest time
url='http://'+address_hass+':8123/api/states/sensor.date_time_iso'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)

hass_time_real = datetime.datetime.strptime(readable_json['state'], '%Y-%m-%dT%H:%M:%S')
hass_time_recorder=datetime.datetime.strptime(readable_json['last_changed'],'%Y-%m-%dT%H:%M:%S.%f%z')

time_now=tz.localize(hass_time_real)
# now = datetime.datetime.now()
# now=now.astimezone(tz)

#get latest state of switch
entity_id='switch.athom_car'
url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
response = get(url, headers=headers)
temp=response.text
temp=temp[1:len(temp)-1]
readable_json=json.loads(temp)

time_array= np.array([])
# state_array=np.array([])
state_array_switch=[]
for i in readable_json:
    try:
        state_array_switch.append(i['state'].lower()=='on')
        time_update=datetime.datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
        time_array=np.append(time_array, time_update.astimezone(tz))
    except:
        print("unknown switch state")
time_array_switch=time_array



# this downloads history of the last day
entity_id='sensor.car_power'
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

# average out over last minutes
idx=time_array>(time_now-datetime.timedelta(minutes=6))
condition1=(len(state_array[idx])>1) and (state_array_switch[-1]==True) and (np.average(state_array[idx])<powerthreshold) and state_array[-1]<powerthreshold

# no recent updates (e.g. because value was constant for a long time)
condition2=(len(state_array[idx])==0) and (time_now-time_array[-1]>datetime.timedelta(minutes=10)) and (state_array[-1]<powerthreshold) and (state_array_switch[-1]==True)

if condition1 or condition2:
    payload='{"entity_id": "switch.athom_car"}'
    url='http://'+address_hass+':8123/api/services/switch/turn_off'
    post(url,data=payload,headers=headers)


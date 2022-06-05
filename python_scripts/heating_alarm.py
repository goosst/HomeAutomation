# turns heating on when house alarm is turned off
# decide between office and living room

import subprocess
import datetime
# from ilock import ILock
from requests import get,post
import json
# from datetime import datetime, timedelta
import datetime
from pytz import timezone
import numpy as np
import pdb

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

#get latest working from home information
entity_id='input_boolean.work_from_home'
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
        print("unknown state")

# last timestap
time_last=time_array[-1]
WorkingFromHome=state_array_switch[-1]

time_stopworking=datetime.time(18,15,0 )
time_stopworking=datetime.datetime.combine(time_now.date(),time_stopworking)
time_stopworking=tz.localize(time_stopworking)

if WorkingFromHome==True and time_now<time_stopworking:
    # turn on heating office
    payload='{"entity_id": "input_boolean.turn_heating_zolder_on"}'
    url='http://'+address_hass+':8123/api/services/input_boolean/turn_on'
    post(url,data=payload,headers=headers)
else:
    # turn on heating living
    payload='{"entity_id": "input_boolean.turn_heating_on"}'
    url='http://'+address_hass+':8123/api/services/input_boolean/turn_on'
    post(url,data=payload,headers=headers)
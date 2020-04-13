# checks if post box is empty
# 12 April 20: initial version, reads raw value in mm sensor.mailbox and converts it to a mailbox state
# - 0: empty
# - 1: full
# - 2: some error

import subprocess
import datetime
# from ilock import ILock
from requests import get,post
import json
# from datetime import datetime, timedelta
import datetime
from pytz import timezone
import numpy as np

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

#get latest Mailbox reading
entity_id='sensor.mailbox'
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
state_last=state_array[-1]

# was latest update recent?
now=datetime.datetime.now().astimezone(tz)
max_delay=datetime.timedelta(minutes=5)

if time_last>now-max_delay:
    #Check if empty (comparison in mm)
    if state_last<100:
        payload='{"state": "Check you post box!"}'
    elif state_last>=100 and state_last<1200:
        payload='{"state": "Post box is empty"}'
    else:
        payload='{"state": "No clue"}'
else:
    payload='{"state": "No update"}'

# Write state of postbox to home assistant
url='http://'+address_hass+':8123/api/states/input_number.mailboxfull'
post(url,data=payload,headers=headers)

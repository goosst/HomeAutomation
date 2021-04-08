# 1. reads alarm clock set by hassalarm, set in variable: input_datetime.next_alarm
# 2. runs actions based on this set time

import subprocess
import datetime
# from ilock import ILock
from requests import get,post
import json
# from datetime import datetime, timedelta
import datetime
from pytz import timezone
import numpy as np
import logging
import os

# import long-live token
import headerfiles as parameters
headers=parameters.headers
address_hass=parameters.address_hass

path="/home/homeassistant/.homeassistant/www"
os.chdir(path)

logging.basicConfig(filename='debug_alarmclock',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.ERROR)
logging.debug("script started")

# check and create dummy variable which keeps track of state of heating
entity_id_trig='input_number.trigger_alarm_turn_heating_on'
entity_id_trig_attic='input_number.trigger_alarm_turn_heating_attic_on'

# get timezone to convert to local time, since database attributes are in UTC time
url='http://'+address_hass+':8123/api/config'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)
time_zone=readable_json['time_zone']
tz = timezone(time_zone)

# get latest time (there might be no advantages over just using now() )
url='http://'+address_hass+':8123/api/states/sensor.date_time_iso'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)

hass_time_real = datetime.datetime.strptime(readable_json['state'], '%Y-%m-%dT%H:%M:%S')
hass_time_recorder=datetime.datetime.strptime(readable_json['last_changed'],'%Y-%m-%dT%H:%M:%S.%f%z')

# time_hass=hass_time_real.astimezone(tz)
time_hass=tz.localize(hass_time_real)
now=datetime.datetime.now().astimezone(tz)

logging.debug("time hass")
logging.debug(time_hass)

# check if an alarm is set through hassalarm and read its date and time
entity_id='input_datetime.next_alarm'
alarm_on=False
try:
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
    response = get(url, headers=headers)
    temp=response.text
    temp=temp[1:len(temp)-1]
    readable_json=json.loads(temp)

    time_array_alarm= np.array([])
    state_array_alarm=np.array([])
    for i in readable_json:
        try:
            state_array_alarm=np.append(state_array_alarm,i['state'])
            time_update=datetime.datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
            time_array_alarm=np.append(time_array_alarm, time_update.astimezone(tz))
        except:
            print("unknown state")
    # last timestap
    time_last_alarm=time_array_alarm[-1] #last time alarm clock was updated
    state_last_alarm=state_array_alarm[-1]
    state_last_alarm=datetime.datetime.strptime(state_last_alarm,'%Y-%m-%d %H:%M:%S')
    alarm_on=True
except:
    # dummy variable was never created, 
    # should be made more robust instead of try except construction
    alarm_on=False
logging.debug("alarm set?")
logging.debug(alarm_on)

logging.debug("time last alarm updated")
logging.debug(time_last_alarm.astimezone(tz))

state_last_alarm=tz.localize(state_last_alarm)
logging.debug("time last alarm")
logging.debug(state_last_alarm)

# ######################################
# where the logic starts to turn on heating in livingroom based on alarm on phone
#########################################


# download dummy variable to keep track of triggering by automation
try:
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id_trig
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
except:
    # dummy variable was not created before, rest api of home assistant creates this automatically when doing a post request
    print("exception state")
    url='http://'+address_hass+':8123/api/states/'+entity_id_trig
    payload='{"state": "new_alarm_set"}'
    post(url,data=payload,headers=headers)

logging.debug("state of trigger flag")
logging.debug(state_last_dummyheater)

# set a flag to indicate a new alarm is set / getting active through hassalarm; this is not the best piece of logic
if time_hass>time_last_alarm and  time_hass<=(time_last_alarm+datetime.timedelta(minutes=12)):
    url='http://'+address_hass+':8123/api/states/'+entity_id_trig
    payload='{"state": "new_alarm_set"}'
    post(url,data=payload,headers=headers)
    logging.debug("new alarm set!")


#get latest temperature livingroom
entity_id='sensor.temperature_living'
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


# Do activities related to alarm
if alarm_on==True:
    # time_alarm=state_last_alarm.astimezone(tz)
    time_alarm=state_last_alarm

    # Turn on heating 55 minutes before alarm clock for 30 minutes
    time_pre_alarm=datetime.timedelta(minutes=55)
    time_on=time_alarm-time_pre_alarm

    time_off=time_alarm-time_pre_alarm+datetime.timedelta(minutes=30)

    logging.debug("time on")
    logging.debug(time_on)
    logging.debug("time off")
    logging.debug(time_off)


    if time_hass>time_on and state_last_dummyheater=='new_alarm_set' and temp_last<16:
        msg2='on'
        payload='{"entity_id": "input_boolean.turn_heating_on"}'
        url='http://'+address_hass+':8123/api/services/input_boolean/turn_'+msg2
        post(url,data=payload,headers=headers)

        logging.debug("turned heating on")

        # if this activity triggered, set a flag in homeassistant to indicate the trigger occured 
        # (this to avoid this script keeps triggering heating when called periodically)
        url='http://'+address_hass+':8123/api/states/'+entity_id_trig
        payload='{"state": "script_execution_ongoing"}'
        post(url,data=payload,headers=headers)
    
    if time_hass>time_off and state_last_dummyheater=='script_execution_ongoing':
        msg2='off'
        payload='{"entity_id": "input_boolean.turn_heating_on"}'
        url='http://'+address_hass+':8123/api/services/input_boolean/turn_'+msg2
        post(url,data=payload,headers=headers)

        logging.debug("turned heating off")

        # if this activity triggered, set a flag in homeassistant to indicate the trigger occured 
        # (this to avoid this script keeps triggering heating when called periodically)
        url='http://'+address_hass+':8123/api/states/'+entity_id_trig
        payload='{"state": "triggered_alarm_heating_off_scripted"}'
        post(url,data=payload,headers=headers)
logging.debug("script living ended")

# ######################################
# where the logic starts to turn on heating on attic based on alarm on phone
# and when working from home
#########################################

# download dummy variable to keep track of triggering by automation
try:
    url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id_trig_attic
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
except:
    # dummy variable was not created before, rest api of home assistant creates this automatically when doing a post request
    print("exception state")
    url='http://'+address_hass+':8123/api/states/'+entity_id_trig_attic
    payload='{"state": "new_alarm_set"}'
    post(url,data=payload,headers=headers)

logging.debug("state of trigger flag")
logging.debug(state_last_dummyheater)

# set a flag to indicate a new alarm is set / getting active through hassalarm; this is not the best piece of logic
if time_hass>time_last_alarm and  time_hass<=(time_last_alarm+datetime.timedelta(minutes=12)):
    url='http://'+address_hass+':8123/api/states/'+entity_id_trig_attic
    payload='{"state": "new_alarm_set"}'
    post(url,data=payload,headers=headers)
    logging.debug("new alarm set!")

#get latest temperature attic
entity_id='sensor.temperature_zolder_vaillant'
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

#get working from home
entity_id='input_boolean.work_from_home'
url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id
response = get(url, headers=headers)
temp=response.text
temp=temp[1:len(temp)-1]
readable_json=json.loads(temp)

time_array= np.array([])
state_array=np.array([])
for i in readable_json:
    try:
        state_array=np.append(state_array,i['state'])
        # time_update=datetime.datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
        # time_array=np.append(time_array, time_update.astimezone(tz))
    except:
        print("unknown state")

# last status
work_from_home=state_array[-1]

# Do activities related to alarm
if alarm_on==True:
    # time_alarm=state_last_alarm.astimezone(tz)
    time_alarm=state_last_alarm

    # Turn on heating x minutes before alarm clock 
    minutes_in_advance=60*(16-temp_last)
    if minutes_in_advance<0:
        minutes_in_advance=2
    time_pre_alarm=datetime.timedelta(minutes=minutes_in_advance)
    time_on=time_alarm-time_pre_alarm

    time_off=time_alarm-time_pre_alarm+datetime.timedelta(minutes=1)

    logging.debug("time on")
    logging.debug(time_on)
    logging.debug("time off")
    logging.debug(time_off)


    if time_hass>time_on and state_last_dummyheater=='new_alarm_set' and temp_last<16 and work_from_home=='on':
        msg2='on'
        payload='{"entity_id": "input_boolean.turn_heating_zolder_on"}'
        url='http://'+address_hass+':8123/api/services/input_boolean/turn_'+msg2
        post(url,data=payload,headers=headers)

        logging.debug("turned heating on")

        # if this activity triggered, set a flag in homeassistant to indicate the trigger occured 
        # (this to avoid this script keeps triggering heating when called periodically)
        url='http://'+address_hass+':8123/api/states/'+entity_id_trig_attic
        payload='{"state": "script_execution_ongoing"}'
        post(url,data=payload,headers=headers)
    
    if time_hass>time_off and state_last_dummyheater=='script_execution_ongoing':
        msg2='off'
        payload='{"entity_id": "input_boolean.turn_heating_on"}'
        url='http://'+address_hass+':8123/api/services/input_boolean/turn_'+msg2
        post(url,data=payload,headers=headers)

        logging.debug("turned heating off")

        # if this activity triggered, set a flag in homeassistant to indicate the trigger occured 
        # (this to avoid this script keeps triggering heating when called periodically)
        url='http://'+address_hass+':8123/api/states/'+entity_id_trig
        payload='{"state": "triggered_alarm_heating_off_scripted"}'
        post(url,data=payload,headers=headers)
logging.debug("script attic ended")

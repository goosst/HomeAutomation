# turns electric heater in bathroom on and off in the morning from home assistant
# 17 nov 19: differentiates between manually turned on and automatically turned on, to decide when to turn heater off
# done by setting a dummy variable through the rest api
# 30 nov 19: checks if alarm was set in the morning
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

# get latest time
url='http://'+address_hass+':8123/api/states/sensor.date_time_iso'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)

hass_time_real = datetime.datetime.strptime(readable_json['state'], '%Y-%m-%dT%H:%M:%S')
hass_time_recorder=datetime.datetime.strptime(readable_json['last_changed'],'%Y-%m-%dT%H:%M:%S.%f%z')

#get latest temperatures
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
try:
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
except:
    # dummy variable was not created before, should be made more robust instead of try except construction
    print("exception state")
    url='http://'+address_hass+':8123/api/states/input_number.dummy_heater'
    payload='{"state": "auto_off"}'
    post(url,data=payload,headers=headers)
    manual_heating=False


legacy_date=False
if legacy_date:
    # check if alarm state is used
    entity_id='sensor.next_alarm'
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
        time_last_alarm=time_array_alarm[-1]
        state_last_alarm=state_array_alarm[-1]
        state_last_alarm=datetime.datetime.strptime(state_last_alarm,'%Y-%m-%d %H:%M:%S')
        if hass_time_real.date()==state_last_alarm.date():
            alarm_on=True
        else:
            alarm_on=False
    except:
        # dummy variable was not created before, should be made more robust instead of try except construction
        alarm_on=False
else:
    # check if alarm state is used
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
        time_last_alarm=time_array_alarm[-1]
        state_last_alarm=state_array_alarm[-1]
        state_last_alarm=datetime.datetime.strptime(state_last_alarm,'%Y-%m-%d %H:%M:%S')
        if hass_time_real.date()==state_last_alarm.date():
            alarm_on=True
        else:
            alarm_on=False
    except:
        # dummy variable was not created before, should be made more robust instead of try except construction
        alarm_on=False

#turn on heater if temp is too low in the morning
#very simplistic formula and clip to a maximum
heating_time=(21-temp_last)*6 #minutes to turn on heating
if heating_time>75:
    heating_time=75

heating_time=datetime.timedelta(minutes=heating_time)


# time_on=datetime.time( 5,20,0 )
# time_on=datetime.datetime.combine(now.date(),time_on)
now=datetime.datetime.now().astimezone(tz)

# time_off=datetime.time( 5,59,0 ) #nachttarrief
time_off=datetime.time(7,15,0 )
time_off=datetime.datetime.combine(now.date(),time_off)
# time_off=time_off.astimezone(tz)
time_off=tz.localize(time_off)

time_on=time_off-heating_time

if time_off>time_on:
	offtime_later_ontime=True
else:
	offtime_later_ontime=False

url='http://'+address_hass+':8123/api/states/input_number.dummy_heater'
if now>time_on and now<time_off and offtime_later_ontime and temp_last<17:
    msg2="ON" # communicate to hass heater was turned on automatically
    payload='{"state": "auto_on"}'
    post(url,data=payload,headers=headers)
elif now>time_off and offtime_later_ontime or temp_last>20:
    msg2="OFF" # communicate to hass heater was turned off automatically
    payload='{"state": "auto_off"}'
    post(url,data=payload,headers=headers)
else:
	msg2="OFF"

if (manual_heating==False):
    print(msg2)
    payload='{"entity_id": "switch.handdoekdroger_control"}'
    url='http://'+address_hass+':8123/api/services/switch/turn_'+msg2
    post(url,data=payload,headers=headers)

    # msg1="mosquitto_pub -h localhost -t cmnd/sonoff/Power1 -u stijn -P mqtt -m "
    # cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
#if (manual_heating==False) and (alarm_on==True):
#    msg1="mosquitto_pub -h localhost -t cmnd/sonoff/Power1 -u stijn -P mqtt -m "
#    cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
#print(msg2)

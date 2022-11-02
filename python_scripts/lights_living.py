# 18 feb 2020: changes lights while starting to watch television 
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

# light bulbs to control

bulbs=['light.tradfri_bulb_s','light.tradfri_bulb_e','light.tradfri_bulb_w','light.tradfri_bulb_n2']

try:
    path="/home/homeassistant/.homeassistant/www"
    os.chdir(path)
except:
    print("no cd to path")

logging.basicConfig(filename='debug_bulbs',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

logging.debug(" -----------------")

# get timezone to convert to local time, since database attributes are in UTC time
url='http://'+address_hass+':8123/api/config'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)
time_zone=readable_json['time_zone']
tz = timezone(time_zone)

# is it dark already?
url='http://'+address_hass+':8123/api/states/sun.sun'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)
sun_state=readable_json['state']

# get state media player (yamaha soundbar)

# yamaha integration depreciated from some homeassistant version
# url='http://'+address_hass+':8123/api/states/media_player.living_room_main'
# response = get(url, headers=headers)

# set by yamaha.py
url='http://'+address_hass+':8123/api/states/input_number.yamaha_input'
response = get(url, headers=headers)
temp=response.text
yamaha_inputsource=json.loads(temp)

# set by yamaha.py
url='http://'+address_hass+':8123/api/states/input_number.yamaha_power'
response = get(url, headers=headers)
temp=response.text
readable_json=json.loads(temp)

# attributes=readable_json['attributes']
time_update=datetime.datetime.strptime(readable_json['last_changed'],'%Y-%m-%dT%H:%M:%S.%f%z')
time_update=time_update.astimezone(tz)

now=datetime.datetime.now().astimezone(tz)
logging.debug(now)

time_since_last_state_change=now-time_update
time_since_last_state_change=time_since_last_state_change.total_seconds()

logging.debug(time_since_last_state_change)

# check if sound bar starts being used for watching tv
# started_watching_tv=False
# if ((readable_json['state']=='idle') and
# (attributes['source']=='tv') and
# (attributes['is_volume_muted']==False) and
# (time_since_last_state_change<time_treshold_change) and
# (sun_state=='below_horizon')):
#     started_watching_tv=True

logging.debug(readable_json['state'])
logging.debug(yamaha_inputsource['state'])
logging.debug(sun_state)

time_treshold_change=9999 #if the last change was later than this, don't change lights
started_watching_tv=False
stopped_watching_tv=True

if ((readable_json['state']=='on')  and (yamaha_inputsource['state']=='tv') and
(time_since_last_state_change<time_treshold_change) and
(sun_state=='below_horizon')):
    started_watching_tv=True
    stopped_watching_tv=False
    logging.debug("soundbar turned on")


if (((readable_json['state']=='off') or (readable_json['state']=='unkown') or (readable_json['state']=='standby') ) and
(time_since_last_state_change<time_treshold_change) and
(sun_state=='below_horizon')):
    stopped_watching_tv=True
    logging.debug("soundbar turned off")


if started_watching_tv==True:
    transition_time=10
    color_temp=430 #min_mireds: 250 (cold), max_mireds: 454 (warm)
    brightness=65

if stopped_watching_tv==True:
    transition_time=15
    color_temp=275 #min_mireds: 250 (cold), max_mireds: 454 (warm)
    brightness=100


# set color_temp of lights
# breakpoint()
if started_watching_tv==True or stopped_watching_tv==True:
    #turn lights on
    for bulb in bulbs:
        url='http://'+address_hass+':8123/api/services/light/turn_on'
        data = {}
        data['entity_id'] = bulb
        data['transition']= transition_time
        if bulb != 'light.tradfri_bulb_n2':
            data['color_temp']=color_temp
        if bulb=='light.tradfri_bulb_s' and started_watching_tv:
            data['brightness_pct']=1
        elif bulb=='light.tradfri_bulb_s' and stopped_watching_tv:
            data['brightness_pct']=50
        else:
            data['brightness_pct']=brightness
        payload = json.dumps(data)
        post(url,data=payload,headers=headers)

# turn off lightbulbs
# for bulb in bulbs:
#     print(bulb)
#     url='http://'+address_hass+':8123/api/states/'+bulb
#     response = get(url, headers=headers)
#     temp=response.text
#     readable_json=json.loads(temp)
#     readable_json['attributes']
#     readable_json['last_updated']
#     readable_json['last_changed']
#     readable_json['state']
#
#     data = {}
#     data['entity_id'] = bulb
#     payload = json.dumps(data)
#
#     url='http://'+address_hass+':8123/api/services/light/turn_off'
#     # payload_start='{"entity_id": "'
#     # payload_end='"}'
#     # payload=payload_start+bulb+payload_end
#     payload_correct='{"entity_id": "light.tradfri_bulb"}'
#     post(url,data=payload,headers=headers)


# get latest time
# url='http://'+address_hass+':8123/api/states/sensor.date_time_iso'
# response = get(url, headers=headers)
# temp=response.text
# readable_json=json.loads(temp)
# hass_time_real = datetime.datetime.strptime(readable_json['state'], '%Y-%m-%dT%H:%M:%S')
# hass_time_recorder=datetime.datetime.strptime(readable_json['last_changed'],'%Y-%m-%dT%H:%M:%S.%f%z')

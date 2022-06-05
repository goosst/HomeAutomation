# May 2022: created python script to run with home assistant and check air pressure and water pressure, much easier to update compared to reflashing the ESP
import subprocess
import datetime
from requests import get,post
import json
from pytz import timezone
import numpy as np
import pdb


# import long-live token
import headerfiles as parameters
headers=parameters.headers
address_hass=parameters.address_hass


# conversion factors 
# mV to Pa: pressure=m*shuntVolt+offset
m=332
offset=82592

grav=9.81 #m/s2
densitywater=1000 #kg/m3


#get latest reading of shunt voltage
entity_id='sensor.water_level_shunt'
# this downloads history of the last day
url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id

response = get(url, headers=headers)
temp=response.text
temp=temp[1:len(temp)-1]
readable_json=json.loads(temp)

# time_array= np.array([])
state_array=np.array([])
for i in readable_json:
    try:
        state_array=np.append(state_array,float(i['state']))
        # time_update=datetime.datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
        # time_array=np.append(time_array, time_update.astimezone(tz))
    except:
        print("unknown state")

shuntVoltageLast=state_array[-1]

PressSensorAct=m*shuntVoltageLast+offset


#get latest reading of air pressure
entity_id='sensor.air_pressure'
# this downloads history of the last day
url='http://'+address_hass+':8123/api/history/period'+'?filter_entity_id='+entity_id

response = get(url, headers=headers)
temp=response.text
temp=temp[1:len(temp)-1]
readable_json=json.loads(temp)

# time_array= np.array([])
state_array=np.array([])
for i in readable_json:
    try:
        state_array=np.append(state_array,float(i['state']))
        # time_update=datetime.datetime.strptime(i['last_updated'],'%Y-%m-%dT%H:%M:%S.%f%z')
        # time_array=np.append(time_array, time_update.astimezone(tz))
    except:
        print("unknown state")

airPressureLatest=state_array[-1]

# water height
waterHeight=(PressSensorAct-airPressureLatest)/(grav*densitywater)

msg1="mosquitto_pub -h localhost -t /sensor/waterlevel/depth -u stijn -P mqtt -m "
cp = subprocess.run([msg1+str(waterHeight)],shell=True,stdout=subprocess.PIPE)

# payload='{"state": "Post box is empty"}'
# payload={"state": waterHeight}
# pdb.set_trace()
# # Write state of water height to home assistant
# url='http://'+address_hass+':8123/api/states/input_number.waterdepth'
# post(url,data=payload,headers=headers)




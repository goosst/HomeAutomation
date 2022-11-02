import subprocess
import time
import logging
import os
from pyamaha import Device, System, Zone, ZONES
from requests import get,post
import json


def update_hass_variables_string( address_hass,headers_hass,number_string,hass_variable ):
    if number_string is None:
        payload='{"state": "NA"}'
    else:
        payload='{"state": "'+str(number_string)+'"}'
    url='http://'+address_hass+':8123/api/states/input_number.'+hass_variable
    post(url,data=payload,headers=headers_hass)


# import long-live token
import headerfiles as parameters
headers=parameters.headers
address_hass=parameters.address_hass

# --------------------------------------------------------------------------------------
# confirm or search ip address of soundbar
# --------------------------------------------------------------------------------------

mac_address='94:e3:6d:61:59:73' #address to search for
# mac_address': {'wired_lan': '00A0DEFEAB5B', 'wireless_lan': '94E36D615973', 'wireless_direct': '94E36D615974'
base_address='192.168.0.' #base of ip address
textfile='myfile.txt'

path="/home/homeassistant/.homeassistant"
os.chdir(path)

# check previously saved value
if os.path.exists(textfile):
    file1 = open(textfile, 'r')
    last_ipaddress=str(file1.read())
    file1.close()

try:
    i=int(last_ipaddress.split('.')[-1])
except:
    i=100

# check mac address and loop over ip addresses if not found
cntr=0
addressfound=False
while True:
    # for some reason the devices far away from the router are only discovered reliably when first pinged before requesting the mac address, yes this is slow
    ipaddress=str(base_address)+str(i)
    cmd="ping "+ipaddress+" -c 3 -W 2"
    if os.system(cmd)==0:
        cmd="arp "+ipaddress
        output=subprocess.check_output(cmd,shell=True)
        if str(output).find(mac_address)!=-1:
            print("mac address found at "+ipaddress)
            if cntr!=-1:
                file1 = open(textfile, 'w')
                file1.write(ipaddress)
                file1.close()
            addressfound=True 
            break
    i=i+1    
    if i>254:
        i=1
    cntr=cntr+1
    if cntr==255:
        break
    


# --------------------------------------------------------------------------------------
# check status sound bar
# --------------------------------------------------------------------------------------

if addressfound:
    DEFAULT_ZONE = ZONES[0]
    dev = Device(ipaddress)
    # res = dev.request(System.get_device_info())
    # res=res.json()
    # print(res)
    # print("-----------------------------------")
    # res1 = dev.request(System.get_network_status())
    # print(res1.json())
    # print("-----------------------------------")
    # res1 = dev.request(System.get_features())
    # print(res1.json())
    # print("-----------------------------------")
    res1 = dev.request(Zone.get_status(DEFAULT_ZONE))
    soundbar_status=res1.json()

    update_hass_variables_string( address_hass,headers,soundbar_status['input'],'yamaha_input')
    update_hass_variables_string( address_hass,headers,soundbar_status['power'],'yamaha_power')
else:
    update_hass_variables_string( address_hass,headers,'unkown','yamaha_input')
    update_hass_variables_string( address_hass,headers,'unkown','yamaha_power')

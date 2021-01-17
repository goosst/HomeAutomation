# 15 May 2020: integration of octoprint in home assistant, standard home assistant component doesn't seem to do anything
#  See documentation REST api of octoprint https://docs.octoprint.org/en/master/api/printer.html
from requests import get,post
import json
import getopt
import sys
import datetime
# from datetime import datetime, timedelta


def update_hass_variables_seconds( address_hass,headers_hass,number_string,hass_variable ):
    if number_string is None:
        payload='{"state": "NA"}'
    else:
        payload='{"state": "'+str(datetime.timedelta(seconds=number_string))+'"}'
    url='http://'+address_hass+':8123/api/states/input_number.'+hass_variable
    post(url,data=payload,headers=headers_hass)



def update_hass_variables_string( address_hass,headers_hass,number_string,hass_variable ):
    if number_string is None:
        payload='{"state": "NA"}'
    else:
        payload='{"state": "'+str(number_string)+'"}'
    url='http://'+address_hass+':8123/api/states/input_number.'+hass_variable
    post(url,data=payload,headers=headers_hass)

# check if passed options are valid
try:
    options, args = getopt.getopt(sys.argv[1:], 'L:',['led_status='])
    print(options)
    print(args)
except getopt.GetoptError:
    print("incorrect syntax")
    print("usage: python3 octoprint.py -L <value>")
    print("default to off degrees")
    msg2='off'
    sys.exit(2)
for opt, value in options:
    if opt in ('-l','-L','--led_status'):
        msg2=value
        print("successful argument")
        print(msg2)


import headerfiles as parameters
headers_octo=parameters.headers_octoprint
address_octo=headers_octo['Host']

headers_hass=parameters.headers
address_hass=parameters.address_hass

# get printjob information octoprint
url='http://'+address_octo+':5000/api/job'
response = get(url, headers=headers_octo)
temp=response.text
job_json=json.loads(temp)

# get printer status
url='http://'+address_octo+':5000/api/printer'
response = get(url, headers=headers_octo)
temp=response.text
printer_json=json.loads(temp)


octo_state=job_json['state']
json_progress=job_json['progress']
# json_progress['completion']
# json_progress['printTime']
# json_progress['printTimeLeft']

json_job=job_json['job']
# json_job['estimatedPrintTime']

# data = {}
# data['command'] = 'M114'
# payload = json.dumps(data)
# url='http://'+address_octo+':5000/api/printer/command'
# response = post(url,data=payload,headers=headers_octo)
# temp=response.text

## report to hass
# print status
payload='{"state": "'+octo_state+'"}'
url='http://'+address_hass+':8123/api/states/input_number.k8400_state'
post(url,data=payload,headers=headers_hass)

# print times

update_hass_variables_seconds( address_hass,headers_hass,json_progress['printTime'],'k8400_printtime_elapsed')
update_hass_variables_seconds( address_hass,headers_hass,json_progress['printTimeLeft'],'k8400_printtime_left')
update_hass_variables_seconds( address_hass,headers_hass,json_job['estimatedPrintTime'],'k8400_printtime_total')

update_hass_variables_string( address_hass,headers_hass,printer_json['temperature']['bed']['actual'],'k8400_bed_temperature')
update_hass_variables_string( address_hass,headers_hass,printer_json['temperature']['tool0']['actual'],'k8400_tool0_temperature')
# update_hass_variables_string( address_hass,headers_hass,printer_json['temperature']['tool1']['actual'],'k8400_tool1_temperature' )

# turn led on or off from printer
entity_id='input_select.led_printer'
url='http://'+address_hass+':8123/api/states/'+entity_id
response = get(url, headers=headers_hass)
temp=response.text
led_state_requested=json.loads(temp)

data = {}
if led_state_requested['state']=='True':
    data['command'] = 'ledon'
else:
    data['command'] = 'ledoff'
payload = json.dumps(data)
url='http://'+address_octo+':5000/api/printer/command'
response = post(url,data=payload,headers=headers_octo)
temp=response.text


# stop printing
entity_id='input_boolean.print_cancel'
url='http://'+address_hass+':8123/api/states/'+entity_id
response = get(url, headers=headers_hass)
temp=response.text
cancelrequest=json.loads(temp)

data = {}
if cancelrequest['state']=='on':
    data['command']='cancel'
    payload = json.dumps(data)
    url='http://'+address_octo+':5000/api/job'
    response = post(url,data=payload,headers=headers_octo)
    temp=response.text

    data['command'] = 'G28'
    payload = json.dumps(data)
    url='http://'+address_octo+':5000/api/printer/command'
    response = post(url,data=payload,headers=headers_octo)
    temp=response.text


entity_id='input_boolean.print_pause_cyclic'
url='http://'+address_hass+':8123/api/states/'+entity_id
response = get(url, headers=headers_hass)
temp=response.text
periodicpause=json.loads(temp)

if periodicpause['state']=='on':
    url='http://'+address_hass+':8123/api/states/sensor.date_time_iso'
    response = get(url, headers=headers_hass)
    temp=response.text
    readable_json=json.loads(temp)
    
    hass_time_real = datetime.datetime.strptime(readable_json['state'], '%Y-%m-%dT%H:%M:%S')
    # pause every hour for 10 minutes
    if hass_time_real.minute<10:
        data['command']='pause'
        data['action']='pause'
        payload = json.dumps(data)
        url='http://'+address_octo+':5000/api/job'
        response = post(url,data=payload,headers=headers_octo)
        temp=response.text
    else:
        data['command']='pause'
        data['action']='resume'
        payload = json.dumps(data)
        url='http://'+address_octo+':5000/api/job'
        response = post(url,data=payload,headers=headers_octo)
        temp=response.text
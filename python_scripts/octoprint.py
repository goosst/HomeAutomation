# 15 May 2020: integration of octoprint in home assistant, standard home assistant component doesn't seem to do anything
#  See documentation REST api of octoprint https://docs.octoprint.org/en/master/api/printer.html
from requests import get,post
import json
import datetime

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

import headerfiles as parameters
headers_octo=parameters.headers_octoprint
address_octo=parameters.address_octoprint

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
update_hass_variables_string( address_hass,headers_hass,printer_json['temperature']['tool1']['actual'],'k8400_tool1_temperature' )

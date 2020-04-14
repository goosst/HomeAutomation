# start playing music over bluetooth, commanded from home assistant through a shell_command
from sh import bluetoothctl
import subprocess
import pexpect
import time
from requests import get,post
import json

# import secret stuff, long-live token, hass ip address, sudo password
import headerfiles as parameters
headers=parameters.headers
address_hass=parameters.address_hass

# turn on soundbar and put in bluetooth mode through home assistant REST interface (maybe not even needed)
cp = subprocess.Popen(["pkill vlc"],shell=True,stdout=subprocess.PIPE)

url='http://'+address_hass+':8123/api/services/media_player/turn_on'
data = {}
data['entity_id'] = 'media_player.living_room_main'
payload = json.dumps(data)
post(url,data=payload,headers=headers)
time.sleep(1)

url='http://'+address_hass+':8123/api/services/media_player/select_source'
data = {}
data['entity_id'] = 'media_player.living_room_main'
data['source'] = 'bluetooth'
payload = json.dumps(data)
post(url,data=payload,headers=headers)
# time.sleep(1)

# connect tinkerboard with soundbar by restarting bunch of bluetooth stuff
child = pexpect.spawn('systemctl restart bluetooth')
child.expect('Password:') #sudo password
child.sendline(parameters.sudo_passw)
time.sleep(3)

cp = subprocess.run(["pulseaudio -k"],shell=True,stdout=subprocess.PIPE)
cp = subprocess.run(["pulseaudio --start"],shell=True,stdout=subprocess.PIPE)
bluetoothctl("agent","off")
bluetoothctl("power","off")
bluetoothctl("power","on")
bluetoothctl("agent","on")
# bluetoothctl("select","00:1A:7D:DA:71:14")
bluetoothctl("select","F0:03:8C:05:F0:DA") #Get this address by: running the commands on your host system 1) bluetoothctl 2) list
bluetoothctl("disconnect", "94:E3:6D:61:59:72") #Get this address by: running the commands on your host system 1) bluetoothctl 2) devices
bluetoothctl("connect", "94:E3:6D:61:59:72")

## VLC stuff

# play a file added in /home/homeassistant/.homeassistant/www/ folder
# enable http stuff to be able to pause and resume and create playlists
cp = subprocess.Popen(["cvlc --no-video '/home/homeassistant/.homeassistant/www/test.mp3' -I http --http-password fubar &"],shell=True,stdout=subprocess.PIPE)



# cp = subprocess.Popen(["cvlc --no-video http://192.168.0.205:8123/local/test.mp3"],shell=True,stdout=subprocess.PIPE)
# cp = subprocess.Popen(["cvlc --no-video /home/stijn/test.mp3 &"],shell=True,stdout=subprocess.PIPE)
# cp = subprocess.Popen(["cvlc -I http --http-password fubar --quiet &"],shell=True,stdout=subprocess.PIPE)

# launch music file and enable http commands
# cp = subprocess.Popen(["cvlc --no-video /home/stijn/test.mp3 -I http --http-password fubar &"],shell=True,stdout=subprocess.PIPE)
# cp = subprocess.Popen(["cvlc --no-video /home/homeassistant/.homeassistant/www/test.mp3 -I http --http-password fubar &"],shell=True,stdout=subprocess.PIPE)

# page = get('http://127.0.0.1:8080/requests/status.xml?command=pl_empty',auth=auth)
# page = get('http://127.0.0.1:8080/requests/status.xml',auth=auth)
# page = get('http://127.0.0.1:8080/requests/status.xml?command=in_play&input=file:///home/stijn/test.mp3',auth=auth)
# page = get('http://127.0.0.1:8080/requests/status.xml?command=pl_pause',auth=auth)
# page = get('http://127.0.0.1:8080/requests/status.xml?command=pl_stop',auth=auth)
# page = get('http://127.0.0.1:8080/requests/status.xml?command=pl_play',auth=auth)

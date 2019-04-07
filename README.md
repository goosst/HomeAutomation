# HomeAutomation

## hardware ebusd adapter
- read here: https://ebus.github.io/adapter/index.en.html
- ordered on the fhem forum, https://forum.fhem.de/index.php/topic,93190.msg857894.html#msg857894
- I've used the based board (which might not have been the best choice)

## install ebusd
It's an awesome tool, it's however a challenge to find your way :).
- installed on raspberry pi 3
- used raspbian lite
- follow these instructions: https://github.com/john30/ebusd-debian/blob/master/README.md
- I've had some weird issues that magically got resolved: https://github.com/john30/ebusd/issues/276
- check with: `dmesg | grep cp210` if the adpater is added to ttUSB0 (only relevant if you're using cp210 as uart device of course)
output should look something like this:
```pi@raspberrypi:/ $ dmesg | grep cp210
[    3.826051] usbcore: registered new interface driver cp210x
[    3.826168] usbserial: USB Serial support registered for cp210x
[    3.834271] cp210x 1-1.3:1.0: cp210x converter detected
[    3.856013] usb 1-1.3: cp210x converter now attached to ttyUSB0
```
- execute the command: `ebusd -f --scanconfig`, to let ebusd find out your connected devices (a wireless thermostat and a vaillant heater in my case), output looks something like this:
```
pi@raspberrypi:/ $ ebusd -f --scanconfig
2019-03-31 13:30:47.528 [main notice] ebusd 3.3.v3.3 started with auto scan
2019-03-31 13:30:47.875 [bus notice] bus started with own address 31/36
2019-03-31 13:30:47.897 [bus notice] signal acquired
2019-03-31 13:30:48.146 [bus notice] new master 03, master count 2
2019-03-31 13:30:53.347 [bus notice] new master 10, master count 3
2019-03-31 13:30:53.410 [update notice] received unknown MS cmd: 1008b5110101 / 093d3c008033390000ff
2019-03-31 13:30:54.523 [update notice] received unknown MS cmd: 1008b5040100 / 0a00ffffffffffffff0080
2019-03-31 13:30:55.347 [update notice] received unknown BC cmd: 10feb51603010000
2019-03-31 13:30:57.436 [update notice] received unknown MS cmd: 1008b51009000000ffffff45ff00 / 0101
2019-03-31 13:30:58.038 [bus notice] scan 08: ;Vaillant;BAI00;0202;9602
2019-03-31 13:30:58.039 [update notice] store 08 ident: done
2019-03-31 13:30:58.039 [update notice] sent scan-read scan.08  QQ=31: Vaillant;BAI00;0202;9602
2019-03-31 13:30:58.039 [bus notice] scan 08: ;Vaillant;BAI00;0202;9602
2019-03-31 13:30:58.565 [main notice] read common config file vaillant/scan.csv
2019-03-31 13:30:58.780 [main notice] read common config file vaillant/general.csv
2019-03-31 13:30:58.918 [main notice] read common config file vaillant/broadcast.csv
2019-03-31 13:30:59.001 [main notice] read scan config file vaillant/08.bai.csv for ID "bai00", SW0202, HW9602
2019-03-31 13:30:59.576 [update notice] sent scan-read scan.08 id QQ=31: 
2019-03-31 13:30:59.756 [update notice] sent scan-read scan.08 id QQ=31: 
2019-03-31 13:30:59.936 [update notice] sent scan-read scan.08 id QQ=31: 
2019-03-31 13:31:00.117 [update notice] sent scan-read scan.08 id QQ=31: 21;17;09;0010011632;1300;378112;N5
2019-03-31 13:31:00.478 [main notice] found messages: 198 (2 conditional on 24 conditions, 0 poll, 9 update)
2019-03-31 13:31:00.645 [update notice] sent scan-read scan.08 id QQ=31: 21;17;09;0010011632;1300;378112;N5
2019-03-31 13:31:00.827 [update notice] sent scan-read scan.08 id QQ=31: 21;17;09;0010011632;1300;378112;N5
2019-03-31 13:31:01.010 [update notice] sent scan-read scan.08 id QQ=31: 21;17;09;0010011632;1300;378112;N5
2019-03-31 13:31:01.189 [update notice] sent scan-read scan.08 id QQ=31: 21;17;09;0010011632;1300;378112;N5
2019-03-31 13:31:01.190 [bus notice] scan 08: ;21;17;09;0010011632;1300;378112;N5
2019-03-31 13:31:03.350 [bus notice] scan 15: ;Vaillant;F3700;0114;6102
2019-03-31 13:31:03.350 [update notice] store 15 ident: done
2019-03-31 13:31:03.350 [update notice] sent scan-read scan.15  QQ=31: Vaillant;F3700;0114;6102
2019-03-31 13:31:03.350 [bus notice] scan 15: ;Vaillant;F3700;0114;6102
2019-03-31 13:31:03.581 [update notice] sent unknown MS cmd: 3115b5090124 / 09013231313732323030
2019-03-31 13:31:03.761 [update notice] sent scan-read scan.15 id QQ=31: 
2019-03-31 13:31:03.941 [update notice] sent scan-read scan.15 id QQ=31: 
2019-03-31 13:31:04.002 [bus notice] max. symbols per second: 114
2019-03-31 13:31:04.120 [update notice] sent scan-read scan.15 id QQ=31: 21;17;22;0020108149;0082;006391;N9
2019-03-31 13:31:04.120 [bus notice] scan 15: ;21;17;22;0020108149;0082;006391;N9
2019-03-31 13:31:04.518 [main notice] read scan config file vaillant/15.f37.csv for ID "f3700", SW0114, HW6102
2019-03-31 13:31:04.858 [main notice] found messages: 345 (2 conditional on 24 conditions, 0 poll, 9 update)
2019-03-31 13:31:05.428 [update notice] received read bai Status02 QQ=10: on;60;75.0;70;65.0
2019-03-31 13:31:07.472 [update notice] received update-write bai SetMode QQ=10: auto;0.0;-;-;1;0;1;0;0;0
2019-03-31 13:31:13.444 [update notice] received read bai Status01 QQ=10: 30.5;30.0;-;25.5;28.5;off
2019-03-31 13:31:17.474 [update notice] received update-write bai SetMode QQ=10: auto;0.0;-;-;1;0;1;0;0;0
```

- in parallel commands with ebusctl can be queried
```pi@raspberrypi:~ $ ebusctl info
version: ebusd 3.3.v3.3
signal: acquired
symbol rate: 23
max symbol rate: 114
min arbitration micros: 3217
max arbitration micros: 3341
min symbol latency: 4
max symbol latency: 5
reconnects: 0
masters: 3
messages: 345
conditional: 2
poll: 0
update: 9
address 03: master #11
address 08: slave #11, scanned "MF=Vaillant;ID=BAI00;SW=0202;HW=9602", loaded "vaillant/bai.0010015600.inc" ([HW=9602]), "vaillant/08.bai.csv"
address 10: master #2
address 15: slave #2, scanned "MF=Vaillant;ID=F3700;SW=0114;HW=6102", loaded "vaillant/15.f37.csv"
address 31: master #8, ebusd
address 36: slave #8, ebusd
```
here you can find the names f37 and bai for the devicenames needed for further usage in ebusd.

- in parallel commands can be queried:
-- to read: examples:
```
ebusctl read Time
14:30:30
```
-- or writing:
```
pi@raspberrypi:~ $ ebusctl write -c f37 Time 14:00:00
done

pi@raspberrypi:~ $ ebusctl read Time
14:00:02
```

## hassbian hass.io homme-assistant
- not confusing at all


## fhem
- it's not the nicest interface but it looks mature and stable
- installation instructions for debian/raspberry: https://debian.fhem.de/ 
- add repository: deb http://debian.fhem.de/nightly/ / in sources.list
```
   sudo wget http://debian.fhem.de/archive.key | apt-key add -
   sudo nano /etc/apt/sources.list
   sudo apt-get update
   sudo apt-get install fhem
```




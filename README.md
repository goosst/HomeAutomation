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
- execute the command: `ebusd -f --scanconfig`, to let ebusd find out your connected devices (a wireless thermostat and a vaillant heater in my case)
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
```ebusctl read Time
14:30:30
```
-- or writing
```pi@raspberrypi:~ $ ebusctl write -c f37 Time 14:00:00
done

pi@raspberrypi:~ $ ebusctl read Time
14:00:02
```




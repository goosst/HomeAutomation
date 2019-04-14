import subprocess
import schedule
import time

def thermostat_read():
    print(time.time())
    #cp = subprocess.run(["date"],shell=True,stdout=subprocess.PIPE)
    cp = subprocess.run(["ebusctl read Time"],shell=True,stdout=subprocess.PIPE)
    cp_string=cp.stdout.decode('utf-8')
    time_read=cp_string[0:8]
    msg1="mosquitto_pub -h localhost -t sensor/thermostat/fubar -u stijn -P mqtt -m "
    print(time_read)

    cp = subprocess.run([msg1+time_read],shell=True,stdout=subprocess.PIPE)

schedule.every(5).minutes.do(thermostat_read)
while True:
    schedule.run_pending()
    time.sleep(10)

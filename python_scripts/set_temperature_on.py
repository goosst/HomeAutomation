import subprocess
import time

msg2="21" #setpoint temperature

msg1="ebusctl write -c f37 Hc1DayTemp "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

msg1="ebusctl write -c f37 Hc1NightTemp "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

time.sleep(60)

#check if it is truly set
cp = subprocess.run(["ebusctl read Hc1DayTemp"],shell=True,stdout=subprocess.PIPE)
temp=cp.stdout
if int(float(temp[0:4]))!=int(msg2):
    # if not set correct
    msg1="ebusctl write -c f37 Hc1DayTemp "
    cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)


cp = subprocess.run(["ebusctl read Hc1NightTemp"],shell=True,stdout=subprocess.PIPE)
temp=cp.stdout
if int(float(temp[0:4]))!=int(msg2):
    # if not set correct
    msg1="ebusctl write -c f37 Hc1NightTemp "
    cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)
else:
    print("setting correct")

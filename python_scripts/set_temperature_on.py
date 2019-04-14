import subprocess

msg2="21" #setpoint temperature 

msg1="ebusctl write -c f37 Hc1DayTemp "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

msg1="ebusctl write -c f37 Hc1NightTemp "
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

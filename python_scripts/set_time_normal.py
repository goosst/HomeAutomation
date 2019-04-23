import subprocess

cp = subprocess.run(["date +%d.%m.%Y.%H:%M:%S"],shell=True,stdout=subprocess.PIPE)
cp_string=cp.stdout.decode('utf-8')
time_system=cp_string[11:19]
date_system=cp_string[0:10]

msg1="ebusctl write -c f37 Time "
cp = subprocess.run([msg1+time_system],shell=True,stdout=subprocess.PIPE)

msg2="ebusctl write -c f37 Date "
cp = subprocess.run([msg2+date_system],shell=True,stdout=subprocess.PIPE)


#ebusctl read Date, 14.04.2019


#cp = subprocess.run(["date"],shell=True,stdout=subprocess.PIPE)
#msg1="ebusctl write -c f37 Time "
#msg2="23:30:00"
#cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

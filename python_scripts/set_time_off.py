import subprocess
import schedule
import time


#cp = subprocess.run(["date"],shell=True,stdout=subprocess.PIPE)
msg1="ebusctl write -c f37 Time "
msg2="23:30:00"
cp = subprocess.run([msg1+msg2],shell=True,stdout=subprocess.PIPE)

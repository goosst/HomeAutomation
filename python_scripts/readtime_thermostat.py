import subprocess
cp = subprocess.run(["date"], stdout=subprocess.PIPE)
cp_string=cp.stdout.decode('utf-8')
time_read=cp_string[11:19]
msg1="mosquitto_pub -h localhost -t sensor/fubar -m "

cp = subprocess.run([msg1+time_read],shell=True,stdout=subprocess.PIPE)

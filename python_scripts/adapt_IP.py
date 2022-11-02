import subprocess
import time
import logging
import os

mac_address='94:e3:6d:61:59:73' #address to search for
# mac_address': {'wired_lan': '00A0DEFEAB5B', 'wireless_lan': '94E36D615973', 'wireless_direct': '94E36D615974'
base_address='192.168.0.' #base of ip address
textfile='myfile.txt'

# check previously saved value
if os.path.exists(textfile):
    file1 = open(textfile, 'r')
    last_ipaddress=str(file1.read())
    file1.close()

try:
    i=int(last_ipaddress.split('.')[-1])
except:
    i=1

# check mac address and loop over ip addresses if not found
cntr=0
addressfound=False
while True:
    # for some reason the devices far away from the router are only discovered reliably when first pinged before requesting the mac address, yes this is slow
    ipaddress=str(base_address)+str(i)
    cmd="ping "+ipaddress+" -c 4 -W 4"
    if os.system(cmd)==0:
        cmd="arp "+ipaddress
        output=subprocess.check_output(cmd,shell=True)
        if str(output).find(mac_address)!=-1:
            print("mac address found at "+ipaddress)
            file1 = open(textfile, 'w')
            file1.write(ipaddress)
            file1.close()
            addressfound=True 
            break
    i=i+1    
    if i>254:
        i=1
    cntr=cntr+1
    if cntr==255:
        break
    





# works but needs admin rights:
# cp = subprocess.Popen(["sudo arp-scan -l | grep 8c:ce:4e:04:5b:ce"],shell=True,stdout=subprocess.PIPE)
# cp = subprocess.Popen(["sudo arp-scan -l | grep 84:f3:eb:e3:87:f5"],shell=True,stdout=subprocess.PIPE)
# cp_string=str(cp.stdout.readlines())

# search_term='192.168.0.'
# search_term_start=cp_string.find(search_term)

# IPADDRESS=cp_string[search_term_start:search_term_start+len(search_term)+3]




# import headerfiles as parameters
# headers=parameters.headers
# address_hass=parameters.address_hass

# child = pexpect.spawn('sudo arp-scan -l')
# child.expect('stijn:') #sudo password
# child.sendline(parameters.sudo_passw)

# import sys
# from datetime import datetime
# from scapy.all import srp,Ether,ARP,conf 

# ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.0.1/24"),timeout=2)
# ans.summary(lambda s,r: r.sprintf("%Ether.src% %ARP.psrc%") )

# for i in range(len(ans)):
#     print(ans[i])
#     ans[i][1][1] 
# breakpoint()
# # def arp_scan(interface, ips):

# 	print("[*] Scanning...") 
# 	start_time = datetime.now()

# 	conf.verb = 0 
# 	ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst = ips), 
# 		     timeout = 2, 
# 		     iface = interface,
# 		     inter = 0.1)

# 	print ("\n[*] IP - MAC") 
# 	for snd,rcv in ans: 
# 		print(rcv.sprintf(r"%ARP.psrc% - %Ether.src%"))
# 	stop_time = datetime.now()
# 	total_time = stop_time - start_time 
# 	print("\n[*] Scan Complete. Duration:", total_time)

# # if __name__ == "__main__":
# arp_scan('wlp2s0','192.168.0.0/24')
# breakpoint()
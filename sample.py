# -*- coding: utf-8 -*-
import paramiko
import re
import time
import os
import urllib
import urllib2
import json
import datetime
import shutil
import ssl
import os
import sys
import matplotlib.pyplot as plt
import time
import random

#ysample = [random.randint(0, 100) for _ in range(1000)]

xdata = []
ydata = []
xdata1 = []
ydata1 = []
xdata2 = []
ydata2 = []
xdata3 = []
ydata3 = []

f = open('myfile', 'w')
plt.show()
axes = plt.gca()
axes.set_xlim(0, 100)
axes.set_ylim(0, 200)
#axes.subplots_adjust(hspace=10)
axes.set_xlabel('time')
axes.set_ylabel('Utilization percentage')
axes.xaxis.label.set_color('red')
axes.yaxis.label.set_color('green')

#axes = plt.add_subplot(1,1,1)
line, = axes.plot(xdata, ydata, 'b-',label='PE11_to_PE21')
line1, = axes.plot(xdata1, ydata1, 'r-',label='PE11_to_PE22')
line2, = axes.plot(xdata2, ydata2, 'g-',label='PE12_to_PE22')
line3, = axes.plot(xdata3, ydata3, 'y-',label= 'PE12_to_PE21')

legend = axes.legend(loc='upper center', shadow=True)

frame = legend.get_frame()
frame.set_facecolor('0.90')


# Create instance of SSHClient object

def connect_ssh(ip,username,password):
  remote_conn_pre = paramiko.SSHClient()
  # Automatically add untrusted hosts (make sure okay for security policy in your environment)
  remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  # initiate SSH connection
  remote_conn_pre.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False,timeout=1000000)
  print "SSH connection established to %s" % ip
  paramiko.util.log_to_file("filename.log")
  remote_conn = remote_conn_pre.invoke_shell()
  print "Interactive SSH session established"
  output = remote_conn.recv(1000)
  return(remote_conn)

def curlFunction(url,diff,auth):
   if diff == 0 :
      diff = 1
   ctx = ssl.create_default_context()
   ctx.check_hostname = False
   ctx.verify_mode = ssl.CERT_NONE
   url = url + str(diff)
   req=urllib2.Request(url, None, {"Authorization": "Bearer %s" %auth})
   req.get_method = lambda: "PUT"
   response=urllib2.urlopen(req,context=ctx)
   html=response.read()
   json_obj=json.loads(html)
   return json_obj


def fetch_tx_pkt(ssh_handler,interface):
   interface = "show router  interface " + interface + " statistics\n"
   m = mpls_tx = ''
   if (ssh_handler.transport is None):
     print("ssh handler is closed")

   while (not m) or (not mpls_tx) :
     ssh_handler.send(interface)
     time.sleep(1)
     output = ssh_handler.recv(5000)
#     print(output)
     m = re.findall("[^ ]Tx Pkts\\s+:\\s+(\\d+)", output)
     mpls_tx = re.findall("[^ ]Mpls Tx Pkts\\s+:\\s+(\\d+)", output)
#     print(mpls_tx)
   if "INT_LAG1_PE12_to_PE22_1" in interface:
     f.write("interface:%s m[0]:%s mpls_tx[0]:%s"%(output,m[0],mpls_tx[0]))
   return (int(m[0])+int(mpls_tx[0]))


PE11 = connect_ssh('135.249.184.67','admin','admin')
os.system('clear')
PE12 = connect_ssh('135.249.184.51','admin','admin')
os.system('clear')
PE21 = connect_ssh('135.249.184.112','admin','admin')
os.system('clear')
PE22 = connect_ssh('135.249.184.106','admin','admin')
os.system('clear')
HNSD = connect_ssh('135.249.184.202','root','mainstreet')
os.system('clear')
print("wait....graph is getting ready!")

HNSD.send("cat /opt/nsp/os/tomcat/conf/system.conf\n")
time.sleep(1)
output = HNSD.recv(5000)
n = re.findall("\\s+system-token=([a-zA-Z0-9]+)", output)
auth = n[0]


diff1_prev = 0
diff2_prev = 0
diff3_prev = 0
diff4_prev = 0



i = 0

while (1) :
   i =  i + 1



   stream1_Tx_PKTS = int(fetch_tx_pkt(PE11,"INT_LAG1_PE11_to_PE21_1"))
   stream2_Tx_PKTS = int(fetch_tx_pkt(PE11,"INT_LAG2_PE11_to_PE22_1"))
   stream3_Tx_PKTS = int(fetch_tx_pkt(PE12,"INT_LAG1_PE12_to_PE22_1"))
   stream4_Tx_PKTS = int(fetch_tx_pkt(PE12,"INT_LAG2_PE12_to_PE21_1"))

   time.sleep(5)

   stream1_Tx_PKTS_curr = int(fetch_tx_pkt(PE11,"INT_LAG1_PE11_to_PE21_1"))
   stream2_Tx_PKTS_curr = int(fetch_tx_pkt(PE11,"INT_LAG2_PE11_to_PE22_1"))
   stream3_Tx_PKTS_curr = int(fetch_tx_pkt(PE12,"INT_LAG1_PE12_to_PE22_1"))
   stream4_Tx_PKTS_curr = int(fetch_tx_pkt(PE12,"INT_LAG2_PE12_to_PE21_1"))

   diff1 = (stream1_Tx_PKTS_curr - stream1_Tx_PKTS)/1000
   diff2 = (stream2_Tx_PKTS_curr - stream2_Tx_PKTS)/1000
   diff3 = (stream3_Tx_PKTS_curr - stream3_Tx_PKTS)/1000
   diff4 = (stream4_Tx_PKTS_curr - stream4_Tx_PKTS)/1000

   f.write('diff1:%s diff2:%s diff3:%s diff4:%s\n'%(diff1,diff2,diff3,diff4))  # python will convert \n to os.linesep

   url1 = "https://135.249.184.202:8543/sdn/api/test/set/interasl3vpn/name/10.10.1.1-eBGP-10.10.1.2/"
   url2 = "https://135.249.184.202:8543/sdn/api/test/set/interasl3vpn/name/10.10.3.1-eBGP-10.10.3.2/"
   url3 = "https://135.249.184.202:8543/sdn/api/test/set/interasl3vpn/name/10.10.4.1-eBGP-10.10.4.2/"
   url4 = "https://135.249.184.202:8543/sdn/api/test/set/interasl3vpn/name/10.10.5.1-eBGP-10.10.5.2/"


   if (diff1<diff1_prev):
       diff1=diff1_prev


   xdata.append(i)
   ydata.append(diff1)
   ydata1.append(diff2)
   ydata2.append(diff3)
   ydata3.append(diff4)

   os.system('clear')
   print ("Interface           Forward")
   print ("                    Direction")
   print ("%10s            %5s percent        "%("PE11_to_PE21",diff1))
   print ("%10s            %5s percent        "%("PE11_to_PE22",diff2))
   print ("%10s            %5s percent        "%("PE12_to_PE22",diff3))
   print ("%10s            %5s percent        "%("PE12_to_PE21",diff4))


  diff1_prev = diff1
  diff2_prev = diff2
  diff3_prev = diff3
  diff4_prev = diff4





   diff1 = diff1 * 10000
   diff2 = diff2 * 10000
   diff3 = diff3 * 10000
   diff4 = diff4 * 10000

   response_1 =  curlFunction(url1,diff1,auth)
   response_2 =  curlFunction(url2,diff2,auth)
   response_3 =  curlFunction(url3,diff3,auth)
   response_4 =  curlFunction(url4,diff4,auth)



   line.set_xdata(xdata)
   line.set_ydata(ydata)

   line1.set_xdata(xdata)
   line1.set_ydata(ydata1)

   line2.set_xdata(xdata)
   line2.set_ydata(ydata2)

   line3.set_xdata(xdata)
   line3.set_ydata(ydata3)


   plt.draw()
   plt.pause(1e-17)



plt.show()
PE11.close()
PE12.close()
PE21.close()
PE22.close()
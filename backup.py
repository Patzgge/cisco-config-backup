import sys
import time
import paramiko
import os
import cmd
import datetime
import re

#set date and time
now = datetime.datetime.now()

#write in log file
sys.stdout = open('backup.log', "a")
print ("===================================================================================")
print (now)

#open authentication file
f = open('authentication')
#find username
for line in f.readlines():
    if "username" in line:
        userlinestring = line.split (" ")
        username = userlinestring[2].strip()
    if "password" in line:
        passlinestring = line.split (" ")
        password = passlinestring[2].strip()
    if "enablesecret" in line:
        enablelinestring = line.split (" ")
        enablesecret = enablelinestring[2].strip()
#close authentication file
f.close()

#start open ip file
f = open('cisco_hosts')
for ip in f.readlines():
    ip = ip.strip()

    #try for ssh timeout
    try:
        #ssh session starts
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password)

        #ssh shell
        chan = client.invoke_shell()
        time.sleep(1)
        #enter enable secret
        chan.send('en\n')
        chan.send(enablesecret +'\n')
        time.sleep(1)
        #terminal lenght for no paging
        chan.send('term len 0\n')
        time.sleep(1)
        #show config
        chan.send('sh run\n')
        time.sleep(10)
        #show vlan.dat
        chan.send('sh vlan\n')
        time.sleep(2)
        #show vlan.dat
        chan.send('sh cdp nei\n')
        time.sleep(2)
        #show vlan.dat
        chan.send('sh lldp nei\n')
        time.sleep(2)
        #write in output
        output = chan.recv(99999)


        #split ssh output in list
        sshoutput = output.split("\r\n")
        #search for hostname in output
        for line in sshoutput:
            if "hostname" in line:
                hostline = line.split (" ")
                hostname = hostline[1]


        #prefix files for backup
        filename_prefix = hostname
        #show output config and write file with prefix, date and time
        filename = "%s_%.2i-%.2i-%i.cisco" % (filename_prefix,now.day,now.month,now.year)
        if os.path.exists("./"+filename):
            print ("filename exists "+filename)
            filename = "%s_%.2i-%.2i-%i_%.2i-%.2i-%.2i" % (filename_prefix,now.day,now.month,now.year,now.hour,now.minute,now.second)
            f = open(filename)
            f.write(output)
            f.close()
            print ("the new filename ist "+filename)
        else:
            f = open(filename)
            f.write(output)
            f.close()
            print ("file was created "+filename)

        #close ssh session
        client.close()

    except:
        print("host not available "+ip)

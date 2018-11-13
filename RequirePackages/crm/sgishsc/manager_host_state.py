#!/usr/bin/env python

from pexpect import run

class manager_host_state(object):
    def __init__(self,bmcuser,bmcpassword,db_location):
        self.bmcuser = bmcuser
	self.bmcpassword = bmcpassword
	self.dblocation = db_location

    def get_host_index_state_pair(self,name,index,myq):
        bmc_ip = []
        try:
            f = open(self.dblocation)
            for line in f:
	        if line.split()[0] == name:
	            bmc_ip = line.split()[3]
	            break
        finally:
            f.close()

        (output,exitstatus) = run("ipmitool -I lanplus -H %s -U %s -P %s power status" % (bmc_ip,self.bmcuser,self.bmcpassword),timeout=0.5,withexitstatus=True)
        if exitstatus == 0:
            if output.strip() == 'Chassis Power is on':
	        myq.put((index,'on'))
	    else:
	        myq.put((index,'off'))
        else:
            myq.put((index,'unknown'))

#!/usr/bin/env python

from pexpect import run
from time import sleep
from functools import partial

myrun = partial(run, timeout=3, withexitstatus=True)

class manager_host_installation(object):
    def __init__(self,bmcuser,bmcpassword, debug=False):
	self.bmcuser = bmcuser
	self.bmcpassword = bmcpassword
	self.debug = debug
	self.base_cmd = "ipmitool -I lanplus -H %s" + " -U " + self.bmcuser + " -P " + self.bmcpassword + " "

    def install_system(self,name,bmcip,myq):
	set_pxe_asfirst_bootevice = (self.base_cmd % bmcip) + "chassis bootdev pxe"
	power_off = (self.base_cmd % bmcip) + "power off"
	power_on = (self.base_cmd % bmcip) + "power on"
	if self.debug:
	    print "set_pxe_asfirst_bootevice = %s" % set_pxe_asfirst_bootevice
	    print "power_off = %s" % power_off
	    print "power_on = %s" % power_on

        (output1,exitstatus1) = myrun(set_pxe_asfirst_bootevice)
        if exitstatus1 != 0:
            myq.put(name)
	    return

        (output2,exitstatus2) = myrun(power_off)
        if exitstatus2 != 0:
            myq.put(name)
	    return

        sleep(10)

        (output3,exitstatus3) = myrun(power_on)
        if exitstatus3 != 0:
            myq.put(name)

    def __power_on_and_off(self,name,bmcip,myq, str1, str2, str3):
	get_power_status = (self.base_cmd % bmcip) + "power status"
	str1 = (self.base_cmd % bmcip) + str2
	if self.debug:
	    print 'get_power_status = %s' % get_power_status
	    print 'str1 = %s' % str1

        (output1,exitstatus1) = myrun(get_power_status)
        if exitstatus1 != 0:
	    myq.put(name)
	    return

	sleep(2)

        if output1.strip() == str3:
	    return

        (output,exitstatus) = myrun(str1)
        if exitstatus != 0:
	    myq.put(name)
	sleep(5)

    def poweron(self, name, bmcip, myq):
	self.__power_on_and_off(name, bmcip, myq, 'power_on', 'power on', 'Chassis Power is on')

    def poweroff(self,name,bmcip,myq):
	self.__power_on_and_off(name, bmcip, myq, 'power_off', 'power off', 'Chassis Power is off')

#!/usr/bin/env python

import os

class manager_host_dhcp(object):
    def __init__(self,dhcpd_conf):
        self.dhcpdconf = dhcpd_conf

    def add_host_dhcp(self,name,mac,magip):
        os.system("sed -i '$i\    host %s {' %s" % (name,self.dhcpdconf))
        os.system("sed -i '$i\        option host-name  \"%s\";' %s" % (name,self.dhcpdconf))
        os.system("sed -i '$i\        hardware ethernet  %s;' %s" % (mac,self.dhcpdconf))
        os.system("sed -i '$i\        fixed-address %s;' %s" % (magip,self.dhcpdconf))
        os.system("sed -i '$i\    }' %s" % self.dhcpdconf)

    def delete_host_dhcp(self,name):
        os.system("sed -i '/host %s {/,+4d' %s" % (name,self.dhcpdconf))

    def replace_hostinfo_dhcp(self,old_name,orig,new):
        os.system("sed -i '/host %s {/,+4s#%s#%s#' %s" % (old_name,orig,new,self.dhcpdconf))

    def delete_allhost_dhcp(self):
	os.system("sed -i '14,$d' %s" % self.dhcpdconf)
	os.system("sed -i '$a}' %s" % self.dhcpdconf)

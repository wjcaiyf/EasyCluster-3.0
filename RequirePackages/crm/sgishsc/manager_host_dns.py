#!/usr/bin/env python

import os

class manager_host_dns(object):
    def __init__(self,dns_conf):
        self.dnsconf = dns_conf

    def add_host_dns(self,name,macip):
        os.system("sed -i '$a\%s\t\tIN A\t\t%s' %s" % (name,macip,self.dnsconf))

    def delete_host_dns(self,name):
        os.system("sed -i '/%s/d' %s" % (name,self.dnsconf))

    def replace_hostinfo_dns(self,old_name,orig,new):
        os.system("sed -i '/%s/s#%s#%s#' %s" % (old_name,orig,new,self.dnsconf))

    def delete_allhost_dns(self):
	os.system("sed -i '11,$d' %s" % self.dnsconf)

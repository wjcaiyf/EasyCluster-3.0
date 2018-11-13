#!/usr/bin/env python

import os
import fileinput
from pexpect import run
from subprocess import (Popen,PIPE)

class manager_host_db(object):
	
    oldname = ''

    def __init__(self,db_location,sort_need=False):
        self.dblocation = db_location
	self.sort_need = sort_need

    def hostifexists_or_changeinfo(self,name,mac,macip,bmcip):
        names = []
        macs = []
        macips = []
        bmcips = []
        changed_items_pair = []
        try:
            f = open(self.dblocation)
            for line in f:
	        names.append(line.split()[0])
	        macs.append(line.split()[1])
	        macips.append(line.split()[2])
	        bmcips.append(line.split()[3])
        finally:
	    f.close()
	
	(output, exitstatus) = run("grep -i -E '%s +%s +%s +%s' %s" % (name,mac,macip,bmcip,self.dblocation),withexitstatus=True)

        if name in names and mac in macs and macip in macips and bmcip in bmcips and not exitstatus:
            return 'host exists'
        if name not in names and mac not in macs and macip not in macips and bmcip not in bmcips:
            return None

        if name in names:
            try:
	        f = open(self.dblocation)
	        for line in f:
	            if line.split()[0] == name:
		        (ori_name,ori_mac,ori_macip,ori_bmcip) = line.split()
			manager_host_db.oldname = ori_name
		        break
            finally:
	        f.close()
            if ori_mac != mac:
	       changed_items_pair.append((ori_mac,mac))
            if ori_macip != macip:
	       changed_items_pair.append((ori_macip,macip))
            if ori_bmcip != bmcip:
	       changed_items_pair.append((ori_bmcip,bmcip))
	    return changed_items_pair
        if mac in macs:
            try:
	        f = open(self.dblocation)
	        for line in f:
	            if line.split()[1] == mac:
		        (ori_name,ori_mac,ori_macip,ori_bmcip) = line.split()
			manager_host_db.oldname = ori_name
		        break
            finally:
	        f.close()
	    changed_items_pair.append((ori_name,name))
            if ori_macip != macip:
	        changed_items_pair.append((ori_macip,macip))
            if ori_bmcip != bmcip:
	        changed_items_pair.append((ori_bmcip,bmcip))
	    return changed_items_pair
        if macip in macips:
            try:
	        f = open(self.dblocation)
	        for line in f:
	            if line.split()[2] == macip:
		        (ori_name,ori_mac,ori_macip,ori_bmcip) = line.split()
			manager_host_db.oldname = ori_name
		        break
            finally:
	        f.close()
	    changed_items_pair.append((ori_name,name))
	    changed_items_pair.append((ori_mac,mac))
            if ori_bmcip != bmcip:
	        changed_items_pair.append((ori_bmcip,bmcip))
	    return changed_items_pair
        if bmcip in bmcips:
            try:
	        f = open(self.dblocation)
	        for line in f:
	            if line.split()[3] == bmcip:
		        (ori_name,ori_mac,ori_macip,ori_bmcip) = line.split()
			manager_host_db.oldname = ori_name
		        break
            finally:
	        f.close()
	    changed_items_pair.append((ori_name,name))
	    changed_items_pair.append((ori_mac,mac))
	    changed_items_pair.append((ori_macip,macip))
	    return changed_items_pair

    def add_host_db(self,name,mac,macip,bmcip):
        f = open(self.dblocation,'a')
        f.write("%s    %s    %s    %s\n" % (name,mac,macip,bmcip))
        f.close()

    def delete_host_db(self,name):
        run("sed -i '/%s/d' %s" % (name,self.dblocation))

    def delete_allhost_db(self):
        run("sed -i '/^[^#]/d' %s" % self.dblocation)

    def replace_hostinfo_db(self,orign,dest):
	run("sed -i '/%s/s,%s,%s,' %s" % (manager_host_db.oldname,orign,dest,self.dblocation))

    def get_hostinfo_from_db(self,name):
        try:
            f = open(self.dblocation)
            for line in f:
	        if line.split()[0] == name:
	            return line.split()
        finally:
	    f.close()

    def return_firsthost_or_none(self):
        if os.path.getsize(self.dblocation) == 0:
            return
	if self.sort_need:
	    return Popen(["grep", self.hostnames_in_db()[0], self.dblocation], 
			stdout=PIPE).communicate()[0].strip().split()
	try:
	    f = open(self.dblocation)
	    return f.readline().strip().split()
	finally:
	    f.close()

    def hostnames_in_db(self):
        tmp = []
	try:
            for line in fileinput.input(self.dblocation):
                tmp.append(line.split()[0])
	finally:
	    fileinput.close()
        hostnames = [host for host in tmp if not host.startswith('#')]
	if self.sort_need:
            return sorted(hostnames)
        return hostnames

    def get_hostname_bmcip_pairs(self,name):
        try:
            f = open(self.dblocation)
	    for line in f:
	        if line.split()[0] == name:
	            return line.split()[0],line.split()[3]
        finally:
	    f.close()

    def get_all_hostname_bmcip_pairs(self):
        hostname_bmcip_pairs = []
        try:
	    f = open(self.dblocation)
	    for line in f:
	        hostname_bmcip_pairs.append((line.split()[0],line.split()[3]))
 	    return hostname_bmcip_pairs
        finally:
	    f.close()

    def get_alliphexs_in_db(self):
        all_iphexs = []
        try:
            f = open(self.dblocation)
            for i in f:
	        ip_hex = Popen("gethostip %s" % i.split()[2],
			      stdout=PIPE,
			      shell=True).communicate()[0].split()[2]
                all_iphexs.append(ip_hex)
        finally:
	    f.close()
        return all_iphexs	    

    def get_iphex_for_selected_host(self,name):
        try:
            f = open(self.dblocation)
            for i in f:
	        if i.split()[0] == name:
	            ip_hex = Popen("gethostip %s" % i.split()[2],
			          stdout=PIPE,
			          shell=True).communicate()[0].split()[2]
        finally:
	    f.close()
        return ip_hex

if __name__ == "__main__":
    test = manager_host_db('/opt/sgishsc/database/computers','/var/lib/tftpboot/pxelinux.cfg')
    print test.hostifexists_or_changeinfo('n001-eth1','00:0c:29:fe:44:1d','172.16.1.1','172.16.40.1')
    print test.hostifexists_or_changeinfo('n001','00:0c:29:fe:44:1d','172.16.1.1','172.16.40.1')
    print test.hostifexists_or_changeinfo('n001-eth1','00:0c:29:89:1d:af','10.0.1.1','10.0.40.1')

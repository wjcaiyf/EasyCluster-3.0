#!/usr/bin/env python

from subprocess import call

class manager_host_runner_inventory(object):
    def __init__(self, runner_inventory_file):
	self.runner_inventory_file = runner_inventory_file

    def add_host_inventory(self, name):
	call("sed -i '$a\%s.ma' %s" % (name, self.runner_inventory_file),shell=True)

    def delete_host_inventory(self,name):
        call("sed -i '/%s/d' %s" % (name, self.runner_inventory_file), shell=True)

    def replace_hostinfo_inventory(self,old_name,orig,new):
        call("sed -i '/%s/s#%s#%s#' %s" % (old_name,orig,new,self.runner_inventory_file), shell=True)

    def delete_allhost_inventory(self):
	call("sed -i '/^[^#]/d' %s" % self.runner_inventory_file, shell=True)

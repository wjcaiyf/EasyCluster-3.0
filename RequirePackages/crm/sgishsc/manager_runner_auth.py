#!/usr/bin/env python

from subprocess import call

class manager_runner_auth(object):
    def __init__(self,runner_file):
	self.runner_file = runner_file

    def get_user_passwd_for_runner(self):
	try:
	    f = open(self.runner_file)
	    return f.readline().split()
	finally:
	    f.close()

    def set_user_passwd_for_runner(self,remote_user,user_passwd):
	call("sed -i '1c\%s\t%s' %s" % (remote_user,user_passwd,self.runner_file),shell=True)

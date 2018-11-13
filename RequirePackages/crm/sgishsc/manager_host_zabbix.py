#!/usr/bin/env python

import fileinput
from pyzabbix import ZabbixAPI

class manager_host_zabbix(object):
    def __init__(self,db_location,zabbix_host,zabbix_user,zabbix_passwd,zabbix_group='HPC'):
	self.db_location = db_location
	self.zabbix_host = zabbix_host
	self.zabbix_user = zabbix_user
	self.zabbix_passwd = zabbix_passwd
	self.zabbix_group = zabbix_group

	self.zapi = ZabbixAPI(self.zabbix_host)
	self.zapi.login(self.zabbix_user,self.zabbix_passwd)

    def delete_host_zabbix(self,hostname):
        try: 
	    host_id = self.zapi.host.get(filter={'name':hostname})[0]['hostid']
	except IndexError:
	    pass
	else:
	    self.zapi.host.delete(host_id)

    def delete_allhost_zabbix(self):
	names = []
	try:
	    for line in fileinput.input(self.db_location):
	        names.append(line.split()[0])
	finally:
	    fileinput.close()
	for name in names:
	    self.delete_host_zabbix(name)

    def add_host_zabbix(self,name,ip):
	# get group HPC's id
	try:
	    gid = self.zapi.hostgroup.create(name=self.zabbix_group)['groupids'][0]
	except:
	    gid = self.zapi.hostgroup.get(filter={'name':self.zabbix_group})[0]['groupid']
	try:
	    self.zapi.host.create(host=name,interfaces=[{'type':1,
						         'main':1,
						         'useip':1,
						         'ip':ip,
						         'dns':'',
						         'port':'10050'}],
						          groups=[{'groupid':gid}],
							  status=1)
	except:
	    pass 

#!/usr/bin/env python

import re
from tkFileDialog import askopenfilename
from tkMessageBox import showerror

class Check_import_file(object):

    def import_file(self):
        message1 = '''
Correct format as follows:
"name   mac   macip  bmcip"'''
	message2 = '''
For example:
node1  macaddress  10.0.1.1  10.0.40.1'''
        filetypes = [
		("All files","*"),
                ("Text Files","*.txt","TEXT"),]
	filename = askopenfilename(filetypes=filetypes)
        if filename:
	    with open(filename) as ofile:
                first_line = ofile.readline().strip().split()
                if len(first_line) != 4:
                    showerror(title='Format Error',message=message1,detail=message2)
                    return (False,None)
                if not (self._check_macaddress(first_line[1]) and self._check_ipaddress(first_line[2]) and self._check_ipaddress(first_line[3])):
                    showerror(title='Format Error',message=message1,detail=message2)
                    return (False,None)
	        return (True,filename)

    def _check_macaddress(self,mac):
        '''
        Validates a mac address
        '''
        valid = re.compile(r'''
                          (^([0-9A-F]{1,2}[-]){5}([0-9A-F]{1,2})$
                          |^([0-9A-F]{1,2}[:]){5}([0-9A-F]{1,2})$
                          |^([0-9A-F]{1,2}[.]){5}([0-9A-F]{1,2})$)
                          ''',
                          re.VERBOSE | re.IGNORECASE)
        return valid.match(mac) is not None

    def _check_ipaddress(self,address):
        '''
        Validates a ipv4 address
        '''
        valid = re.compile('''^((?:(2[0-4]\d)|(25[0-5])|([01]?\d\d?))\.){3}(?:(2[0-4]\d)|(255[0-5])|([01]?\d\d?))$''',
                          re.VERBOSE | re.IGNORECASE)
        return valid.match(address) is not None

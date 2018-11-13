#!/usr/bin/env python

import os
import re
import sys
import ttk
import os.path
from Tkinter import *
from tkFont import Font
from pexpect import run
from ttk import Combobox
from subprocess import (call,Popen,PIPE,STDOUT)
from threading import Thread
from PIL import (Image,ImageTk)
from ConfigParser import ConfigParser
from ConfigParser import (NoSectionError,NoOptionError)
from tkFileDialog import askopenfile
from tkFileDialog import askopenfilename
from tkMessageBox import showerror
from tkMessageBox import showinfo
from tkMessageBox import showwarning
from tkMessageBox import askokcancel
from sgishsc.manager_host_db import manager_host_db
from sgishsc.manager_host_dns import manager_host_dns
from sgishsc.manager_host_dhcp import manager_host_dhcp
from sgishsc.manager_host_state import manager_host_state
from sgishsc.manager_host_zabbix import manager_host_zabbix
from sgishsc.manager_host_installation import manager_host_installation
from sgishsc.check_import_file import Check_import_file
from sgishsc.manager_runner_auth import manager_runner_auth
from sgishsc.manager_host_runner_inventory import manager_host_runner_inventory
from multiprocessing import (Process,Queue)
########## get values ###########################################################
crm_configure_file = '/etc/crm/crm.conf'
cf = ConfigParser()
cf.read(crm_configure_file)

user = cf.get('AuthIPMI','User')
password = cf.get('AuthIPMI','Password')

dc = cf.get('dhcp','dhcp_configure_file')
restart_dhcp = cf.get('dhcp','restart_dhcp_command')

dnsc = cf.get('dns','zone_ma_file')
restart_dns = cf.get('dns','restart_dns_command')

db_file = cf.get('database','database_file')
sort_need = cf.getboolean('database','display_sort')

tftp_root_dir = cf.get('tftp','tftp_root_dir')
pxeconfigdir = os.path.join(tftp_root_dir,'pxelinux.cfg')
tftp_rhel_config_dir = cf.get('tftp','tftp_rhel_config_dir')
tftp_sles_config_dir = cf.get('tftp','tftp_sles_config_dir')
ks_file_source_dir = cf.get('tftp','ks_file_source_dir')

web_root_dir = cf.get('web','web_root_dir')
ks_file_source_gui = os.path.join(ks_file_source_dir,'rhel_gui.cfg')
ks_file_source_gui = os.path.realpath(ks_file_source_gui)
ks_file_source_text = os.path.join(ks_file_source_dir,'rhel_text.cfg')
ks_file_source_text = os.path.realpath(ks_file_source_text)
ks_file = os.path.join(web_root_dir,'ks/rhel.cfg')

IMAGESDIR = cf.get('misc','images_dir')

use_zabbix = cf.getboolean('zabbix','use_zabbix')
zabbix_host = cf.get('zabbix','zabbix_host')
zabbix_user = cf.get('zabbix','zabbix_user')
zabbix_passwd = cf.get('zabbix','zabbix_passwd')
support_ostype = cf.get('misc','support_ostype').split(',')
support_ostype = [ i.strip().lower() for i in support_ostype]
runner_root_dir = cf.get('misc', 'runner_root_dir')
runner_auth_file = os.path.join(runner_root_dir, 'auth/runner_auth')
runner_inventory_dir = os.path.join(runner_root_dir, 'inventory')
runner_inventory_hosts = os.path.join(runner_inventory_dir, 'hosts')
runner_tmp_inventory_hosts = os.path.join(runner_inventory_dir, 'tmp_hosts')
########## create instance ###########################################################
cif = Check_import_file()
manager_auth = manager_runner_auth(runner_auth_file)
manager_inventory = manager_host_runner_inventory(runner_inventory_hosts)
manager_db = manager_host_db(db_file,sort_need)
manager_dhcp = manager_host_dhcp(dhcpd_conf=dc)
manager_dns = manager_host_dns(dns_conf=dnsc)
manager_state = manager_host_state(user,password,db_file)
manager_install = manager_host_installation(user,password)
if use_zabbix:
    from pyzabbix import ZabbixAPIException
    from requests.exceptions import ConnectionError
    from requests.exceptions import HTTPError
    try:
        manager_zabbix = manager_host_zabbix(db_file,zabbix_host,zabbix_user,zabbix_passwd)
    except (ZabbixAPIException,ConnectionError,HTTPError) as e:
	showerror(title='Zabbix Connection Error',message=e)
	sys.exit(1)
else:
    manager_zabbix = False
######################################################################################

HD_IMAGE = os.path.join(IMAGESDIR,'HostDefinition.jpg')
NH_IMAGE = os.path.join(IMAGESDIR,'NewHost.png')
IMPORT_IMAGE = os.path.join(IMAGESDIR,'Import.jpg')
EXIT_IMAGE = os.path.join(IMAGESDIR,'exit.jpg')
RL_IMAGE = os.path.join(IMAGESDIR,'Reload.jpg')
STAR_IMAGE = os.path.join(IMAGESDIR,'Star.jpg')
CONFIRM_IMAGE = os.path.join(IMAGESDIR,'Confirm.jpg')
QUIT_IMAGE = os.path.join(IMAGESDIR,'Quit.jpg')
REFRESH_IMAGE = os.path.join(IMAGESDIR,'Refresh.jpg')
EDIT_IMAGE = os.path.join(IMAGESDIR,'Edit.jpg')
POWERON_IMAGE = os.path.join(IMAGESDIR,'Poweron.jpg')
POWEROFF_IMAGE = os.path.join(IMAGESDIR,'Poweroff.jpg')
TM_IMAGE = os.path.join(IMAGESDIR,'TransMission.jpg')
DELETE_IMAGE = os.path.join(IMAGESDIR,'Delete.jpg')
RIGHT_IMAGE = os.path.join(IMAGESDIR,'Right.png')
HOSTS_IMAGE = os.path.join(IMAGESDIR,'Hosts.jpg')
AUTOCF_IMAGE = os.path.join(IMAGESDIR,'AutoCF.jpg')
AUTH_IMAGE = os.path.join(IMAGESDIR, 'Auth.jpg')
RUN_IMAGE = os.path.join(IMAGESDIR, 'Run.jpg')
###############################################################################################
class Sgishsc(object):
    def __init__(self,width=700,height=500):
	self.width=width
	self.height=height
        self.root = Tk()
	self.screen_width=self.root.winfo_screenwidth()
	self.screen_height=self.root.winfo_screenheight()
	self.x = ((self.screen_width - self.width) / 2)
	self.y = (((self.screen_height - self.height) / 2) / 2)
        self.root.geometry('%sx%s+%s+%s' % (self.width,self.height,self.x,self.y))
        self.root.resizable(1, 1)  
        self.root.title('Cluster Manager')
	######  image #############################################
	self.image_hd = Image.open(HD_IMAGE)
	self.image_nh = Image.open(NH_IMAGE)
	self.image_import = Image.open(IMPORT_IMAGE)
	self.image_exit = Image.open(EXIT_IMAGE)
	self.image_rl = Image.open(RL_IMAGE)
	self.image_star = Image.open(STAR_IMAGE)
	self.image_confirm = Image.open(CONFIRM_IMAGE)
	self.image_quit = Image.open(QUIT_IMAGE)
	self.image_refresh = Image.open(REFRESH_IMAGE)
	self.image_edit = Image.open(EDIT_IMAGE)
	self.image_poweron = Image.open(POWERON_IMAGE)
	self.image_poweroff = Image.open(POWEROFF_IMAGE)
	self.image_tm = Image.open(TM_IMAGE)
	self.image_delete = Image.open(DELETE_IMAGE)
	self.image_right = Image.open(RIGHT_IMAGE)
	self.image_hosts = Image.open(HOSTS_IMAGE)
	self.image_autocf = Image.open(AUTOCF_IMAGE)
	self.image_auth = Image.open(AUTH_IMAGE)
	self.image_run = Image.open(RUN_IMAGE)

	self.photo_hd = ImageTk.PhotoImage(self.image_hd)
	self.photo_nh = ImageTk.PhotoImage(self.image_nh)
	self.photo_import = ImageTk.PhotoImage(self.image_import)
	self.photo_exit = ImageTk.PhotoImage(self.image_exit)
	self.photo_rl = ImageTk.PhotoImage(self.image_rl)
	self.photo_star = ImageTk.PhotoImage(self.image_star)
	self.photo_confirm = ImageTk.PhotoImage(self.image_confirm)
	self.photo_quit = ImageTk.PhotoImage(self.image_quit)
	self.photo_refresh = ImageTk.PhotoImage(self.image_refresh)
	self.photo_edit = ImageTk.PhotoImage(self.image_edit)
	self.photo_poweron = ImageTk.PhotoImage(self.image_poweron)
	self.photo_poweroff = ImageTk.PhotoImage(self.image_poweroff)
	self.photo_tm = ImageTk.PhotoImage(self.image_tm)
	self.photo_delete = ImageTk.PhotoImage(self.image_delete)
	self.photo_right = ImageTk.PhotoImage(self.image_right)
	self.photo_hosts = ImageTk.PhotoImage(self.image_hosts)
	self.photo_autocf = ImageTk.PhotoImage(self.image_autocf)
	self.photo_auth = ImageTk.PhotoImage(self.image_auth)
	self.photo_run = ImageTk.PhotoImage(self.image_run)
	###########################################################
	
        self.label_font = Font(self.root,family="Helvetica",size=12,weight='bold')
        self.listbox_font = Font(self.root,family="Helvetica",size=10)
        self.common1_font = Font(self.root,family="Helvetica",size=12,weight='bold')
        self.common2_font = Font(self.root,family="Helvetica",size=10)
        self.common3_font = Font(self.root,family="Helvetica",size=10,weight='bold')
	self.common4_font = Font(self.root,family="Helvetica",size=12,weight='bold')
        self.common5_font = Font(self.root,family="Helvetica",size=10)

	self._append_import = IntVar()
	self._append_import.set(1)
	self._passwd_visible = IntVar()
	self._passwd_visible.set(0)
	self._keeped_host = IntVar()
	self._keeped_host.set(0)
	self._with_gui = IntVar()
	self._with_gui.set(0)
	self.ostype = StringVar()
	self.ostype.set('')
	self.module_name = StringVar()
	self.module_name.set('ping')
	
        # Menu
	self.menubar = Menu(self.root, bg='purple')
        self.filemenu = Menu(self.menubar,tearoff=1,bg='white')
	self.filemenu.add_command(label=' New Host',
				  accelerator='Ctrl+N',
				  image=self.photo_nh,
				  compound=LEFT,
				  command=self._add_host_dialog)
	self.filemenu.add_checkbutton(label='Append Import',
				  variable=self._append_import, onvalue=1,)	
	self.filemenu.add_command(label=' Import Host From File',
				  accelerator='Ctrl+I',
				  image=self.photo_import,
				  compound=LEFT,
				  command=self._import_host)
	self.filemenu.add_separator()
	self.filemenu.add_command(label=' Quit',
				  accelerator='Alt+F4',
				  image=self.photo_exit,
			          compound=LEFT,
				  command=self.root.destroy)
        self.helpmenu = Menu(self.menubar,tearoff=1)
	self.helpmenu.add_command(label=' About',
				  image=self.photo_star,
			          compound=LEFT,
				  command=self._about_cluster_manager)
	self.globalmenu = Menu(self.root, tearoff=1)
	self.globalmenu.add_command(label=' Runner Auth',
				  accelerator='Ctrl+A',
				  image=self.photo_auth,
				  compound=LEFT,
				  command=self._edit_authentication)
	self.globalmenu.add_command(label=' reload',
				  accelerator='Ctrl+R',
				  image=self.photo_rl,
				  compound=LEFT,
				  command=self._reload)

        self.menubar.add_cascade(label='File', underline=0, menu=self.filemenu)
        self.menubar.add_cascade(label='Global', underline=0, menu=self.globalmenu)
        self.menubar.add_cascade(label='Help', underline=0, menu=self.helpmenu)

	self.root.config(menu=self.menubar)
        
	self.fm_for_hosts_lb = Frame(self.root)
	self.fm_for_hosts_lb.pack(fill=X)
        self.hosts_lb = Label(self.fm_for_hosts_lb,text='  Hosts',image=self.photo_hosts,compound=LEFT,font=self.label_font)
	self.hosts_lb.pack(side=LEFT,padx=5,pady=2)

        # Left Area
	self.fm_left = Frame(self.root)
        self.listbox = Listbox(self.fm_left,width=20,bd=8,
	             relief=RIDGE,selectmode=EXTENDED,font=self.listbox_font,
		     selectbackground='orange')
	self.listbox.pack(side=LEFT,fill=Y,expand=True)
	self.listbox.insert(END,'Computers')

        self.scb = Scrollbar(self.fm_left,width=10)
	self.scb.pack(side=LEFT,fill=Y)
	self.listbox.config(yscrollcommand=self.scb.set)
	self.scb.config(command=self.listbox.yview)
	self.fm_left.pack(side=LEFT,fill=Y)

	# Right Area
	self.fm_right = Frame(self.root)
	self.fm_right.pack(side=LEFT,fill=BOTH,expand=True)
	self.nb = ttk.Notebook(self.fm_right)
        self.nb.pack(fill=BOTH, expand=True)
        self.tab1 = Frame(self.nb)
        self.tab2 = Frame(self.nb)
        self.nb.add(self.tab1, text='Common')
        self.nb.add(self.tab2, text='Runner')
	

	self.fm_right_down = Frame(self.tab1)
	self.fm_right_down.pack(side=BOTTOM,fill=BOTH,expand=True)

	self.fm_right_up = Frame(self.tab1)
	self.fm_right_up.pack(side=BOTTOM,fill=BOTH,expand=True)

	self.label_hostinfo = Label(self.fm_right_up,text=' Host Manager',
				font=self.common1_font,
				image=self.photo_hd,
				compound=LEFT)
	self.label_hostinfo.pack(pady=10)

	self.fm_name = Frame(self.fm_right_up)
	self.label_name = Label(self.fm_name, text='Name: ',width=5)
	self.label_name.pack(side=LEFT,padx=5,pady=5)
	self.entry_name = Entry(self.fm_name,font=self.common3_font)
	self.entry_name.pack(side=LEFT,fill=X,expand=True)
	self.fm_name.pack(fill=X)

	self.fm_macip = Frame(self.fm_right_up)
	self.label_mac = Label(self.fm_macip, text='Mac: ',width=5)
	self.label_mac.pack(side=LEFT,padx=5,pady=5)
	self.entry_mac = Entry(self.fm_macip,font=self.common3_font)
	self.entry_mac.pack(side=LEFT,fill=X, expand=True)
	self.label_macip = Label(self.fm_macip, text='MacIP: ')
	self.label_macip.pack(side=LEFT,padx=5,pady=5)
	self.entry_macip = Entry(self.fm_macip,font=self.common3_font)
	self.entry_macip.pack(side=LEFT,fill=X, expand=True)
	self.fm_macip.pack(fill=X)

	self.fm_bmcip = Frame(self.fm_right_up)
	self.label_bmcip = Label(self.fm_bmcip, text='BMCIP: ',width=5)
	self.label_bmcip.pack(side=LEFT,padx=5,pady=5)
	self.entry_bmcip = Entry(self.fm_bmcip,font=self.common3_font)
	self.entry_bmcip.pack(side=LEFT,fill=X,expand=True)
	self.fm_bmcip.pack(fill=X)

	self.fm_button = Frame(self.fm_right_up)
	self.bt_confirm = Button(self.fm_button,text="Confirm",
				font=self.common2_font,
				activebackground='green',
				anchor=W,
				image=self.photo_confirm,
			        compound=LEFT,
				underline='0',
				command=self._confirm)
	self.bt_confirm.pack(side=RIGHT,padx=5)
	self.fm_button.pack(fill=X)

	self.separator = Frame(self.fm_right_up,height=2,bd=1,relief=SUNKEN)
	self.separator.pack(fill=X,padx=5,pady=20)

	self.fm_ostype = Frame(self.fm_right_up)
	self.fm_ostype.pack(fill=X,expand=True)
	self.lb_ostype = Label(self.fm_ostype,text='OS Type:',font=self.common4_font)
	self.lb_ostype.pack(side=LEFT,padx=5)


	self.cb = Combobox(self.fm_ostype,value=support_ostype,
			   textvariable=self.ostype,state='readonly',
			   width=10)
	self.cb.pack(side=LEFT)

	self.ckb_with_gui_or_not = Checkbutton(self.fm_ostype, text='with gui', onvalue=1,
					       variable=self._with_gui)

	self.fm_select_autoinst=Frame(self.fm_right_up)
	self.fm_select_autoinst.pack(fill=BOTH,expand=True)
	self.bt_select_autoinst = Button(self.fm_select_autoinst,
		text='AutoXML',font=self.common2_font,
		command=self._select_configfile,activebackground='yellow',
		image=self.photo_autocf,compound=LEFT,width=95)
	self.bt_select_autoinst.pack(side=LEFT,padx=5,pady=2)


	self.fm_yellow = Frame(self.fm_right_down)
	self.separator = Frame(self.fm_right_down,height=2,bd=1,relief=SUNKEN)
	self.separator.pack(fill=X,padx=5,pady=5)
	self.lb_yellow = Label(self.fm_yellow, text='Blue',bg='blue',
				width=8,anchor=W)
	self.lb_yellow.pack(side=LEFT,padx=10,pady=5)
	self.lb_yellow.desc = Label(self.fm_yellow,text='unknown',anchor=W)
	self.lb_yellow.desc.pack(side=LEFT)
	self.bt_quit = Button(self.fm_yellow,width='70',anchor=W,text='Quit',command=self.root.destroy,font=self.common2_font,image=self.photo_quit,compound=LEFT,activebackground='red', underline='0')
	self.bt_quit.pack(anchor=E, ipadx=5,padx=5,pady=5)
	self.fm_yellow.pack(side=BOTTOM,fill=X)

	self.fm_red = Frame(self.fm_right_down)
	self.lb_red = Label(self.fm_red, text='Red',bg='red',
				width=8,anchor=W)
	self.lb_red.pack(side=LEFT,padx=10,pady=5)
	self.lb_red.desc = Label(self.fm_red,text='Power is off',anchor=W)
	self.lb_red.desc.pack(side=LEFT)
	self.fm_red.pack(side=BOTTOM,fill=X)

	self.fm_green = Frame(self.fm_right_down)
	self.lb_green = Label(self.fm_green, text='Green',bg='green',
				width=8,anchor=W)
	self.lb_green.pack(side=LEFT,padx=10,pady=5)
	self.lb_green.desc = Label(self.fm_green,text='Power is on',anchor=W)
	self.lb_green.desc.pack(side=LEFT)
	self.fm_green.pack(side=BOTTOM,fill=X)

	self.fm_color_desc = Frame(self.fm_right_down)
	#self.lb_color_desc = Label(self.fm_color_desc,text='Host Color Description: ', font=self.common1_font)
	#self.lb_color_desc.pack(side=LEFT,padx=10)
	self.fm_color_desc.pack(side=BOTTOM,fill=X)


	self.fm_module_and_args = Frame(self.tab2)
	self.fm_module_and_args.pack(fill=X)
	self.fm_module = Frame(self.fm_module_and_args)
	self.fm_module.pack(fill=X)
	self.lb_module = Label(self.fm_module, text='Module: ')
	self.cb_in_tab2 = Combobox(self.fm_module,value=('ping','shell','copy'),
			   textvariable=self.module_name,state='readonly',
			   width=5)
	self.lb_module.pack(side=LEFT,pady=5)
	self.cb_in_tab2.pack(side=LEFT)
	
	self.fm_shell_commands = Frame(self.fm_module_and_args)
	self.lb_shell_commands = Label(self.fm_shell_commands,text='Commands: ')
	self.entry_shell_commands = Entry(self.fm_shell_commands, font=self.common4_font, width=40)
	self.lb_shell_commands.pack(side=LEFT)
	self.entry_shell_commands.pack(side=LEFT,fill=X)

	self.fm_copy_args = Frame(self.fm_module_and_args)
	self.lb_copy_local = Label(self.fm_copy_args,text='Local: ')
	self.lb_copy_local.pack(side=LEFT)
	self.entry_copy_local = Entry(self.fm_copy_args, font=self.common4_font, width=23)
	self.entry_copy_local.pack(side=LEFT)
	self.lb_copy_dest = Label(self.fm_copy_args,text='Dest: ')
	self.lb_copy_dest.pack(side=LEFT)
	self.entry_copy_dest = Entry(self.fm_copy_args, font=self.common4_font, width=23)
	self.entry_copy_dest.pack(side=LEFT)

	self.fm_sp_between_module_results = Frame(self.tab2, height=2, bd=1, relief=SUNKEN)  
        self.fm_sp_between_module_results.pack(fill=X, padx=2, pady=2)  

	self.fm_results = Frame(self.tab2)
	self.fm_results.pack(fill=X)
	self.bt_show_keeped_hosts = Button(self.fm_results, text='show keeped hosts', command=self._show_keeped_hosts)
	self.bt_run = Button(self.fm_results,text='Run',
			    underline='0',
			    image=self.photo_run,
			    compound=LEFT,
			    activebackground='green',
			    command=self._run_action)
	self.cbt_keeped_hosts = Checkbutton(self.fm_results, text='Keep Host', onvalue=1,
					    variable=self._keeped_host,
					    command=self._do_keep_host)
	self.cbt_keeped_hosts.pack(side=LEFT)
	self.bt_run.pack(side=LEFT,padx=5)

        self.fm_listbox_sbv = Frame(self.tab2)
	self.fm_listbox_sbv.pack(fill=BOTH,expand=True)
	self.fm_sbh = Frame(self.tab2)
	self.fm_sbh.pack(fill=X)

	self.listbox_in_tab2 = Listbox(self.fm_listbox_sbv,selectmode=EXTENDED)
	self.listbox_in_tab2.pack(side=LEFT,fill=BOTH,expand=True)
	self.sbv = Scrollbar(self.fm_listbox_sbv, orient=VERTICAL)
	self.sbv.pack(side=LEFT,fill=Y)
	self.sbh = Scrollbar(self.fm_sbh, orient=HORIZONTAL)
	self.sbh.pack(fill=X)

	self.sbv.config(command=self.listbox_in_tab2.yview)
	self.sbh.config(command=self.listbox_in_tab2.xview)
	self.listbox_in_tab2.config(xscrollcommand=self.sbh.set,
				    yscrollcommand=self.sbv.set)
	#=====================================================================================================
	# event processing
	#=====================================================================================================
	self.root.bind('<Control-n>', lambda event: self._add_host_dialog())
	self.root.bind('<Control-N>', lambda event: self._add_host_dialog())
	self.root.bind('<Control-i>', lambda event: self._import_host())
	self.root.bind('<Control-I>', lambda event: self._import_host())
	self.root.bind('<Control-r>', lambda event: self._reload())
	self.root.bind('<Control-R>', lambda event: self._reload())
	#self.root.bind('<Return>',lambda event: self._run_action())
	self.listbox.bind("<Button-3>", self._popup)
	self.listbox.bind("<Double-Button-1>", self._display_cursel_host_info)
	self.cb.bind('<<ComboboxSelected>>', self._notice_to_select_autoxmlfile)
	self.cb_in_tab2.bind('<<ComboboxSelected>>', self._add_another_widget_or_not)
	self.entry_name.bind('<Control-u>', lambda event: self.entry_name.delete(0,END))
	self.entry_name.bind('<Control-U>', lambda event: self.entry_name.delete(0,END))
	self.entry_mac.bind('<Control-u>', lambda event: self.entry_mac.delete(0,END))
	self.entry_mac.bind('<Control-U>', lambda event: self.entry_mac.delete(0,END))
	self.entry_macip.bind('<Control-u>', lambda event: self.entry_macip.delete(0,END))
	self.entry_macip.bind('<Control-U>', lambda event: self.entry_macip.delete(0,END))
	self.entry_bmcip.bind('<Control-u>', lambda event: self.entry_bmcip.delete(0,END))
	self.entry_bmcip.bind('<Control-U>', lambda event: self.entry_bmcip.delete(0,END))
	self.entry_shell_commands.bind('<Control-u>', lambda event: self.entry_shell_commands.delete(0,END))
	self.entry_shell_commands.bind('<Control-U>', lambda event: self.entry_shell_commands.delete(0,END))
	self.entry_copy_local.bind('<Control-u>', lambda event: self.entry_copy_local.delete(0,END))
	self.entry_copy_local.bind('<Control-U>', lambda event: self.entry_copy_local.delete(0,END))
	self.entry_copy_dest.bind('<Control-u>', lambda event: self.entry_copy_dest.delete(0,END))
	self.entry_copy_dest.bind('<Control-U>', lambda event: self.entry_copy_dest.delete(0,END))
	#======================================================================================================
        # read hosts from db and get host state
	#======================================================================================================
	if not manager_db.return_firsthost_or_none():
	    pass
	else:
	    (fir_name,fir_mac,fir_macip,fir_bmcip) = manager_db.return_firsthost_or_none()
	    self.entry_name.insert(END,fir_name)
	    self.entry_mac.insert(END,fir_mac)
	    self.entry_macip.insert(END,fir_macip)
	    self.entry_bmcip.insert(END,fir_bmcip)

        for host in manager_db.hostnames_in_db():
            self.listbox.insert(END,"    |_%s" % host)
	call('rm -rf %s' % runner_tmp_inventory_hosts, shell=True)

        self._set_item_color()

    def _delete_select(self):
	cursel = list(self.listbox.curselection())
	if cursel == ['0']:
	    anwser = askokcancel(title='Delete all',message='All hosts will be deleted, are you sure?')
	    if anwser:
	        manager_dhcp.delete_allhost_dhcp()
	        manager_dns.delete_allhost_dns()
		manager_inventory.delete_allhost_inventory()
		if manager_zabbix:
		    manager_zabbix.delete_allhost_zabbix()
		manager_db.delete_allhost_db()
	        self.listbox.delete(1,END)
	        for i in manager_db.get_alliphexs_in_db():
	            call("rm -rf %s/%s" % (pxeconfigdir,i),shell=True)
	        showinfo(title='Delete all',message='All hosts are deleted')
	else: 
	    if len(cursel) == 1:
	        anwser = askokcancel(title='Delete Host',message='Host selected will be deleted, Are you sure?')
	    else:
	        anwser = askokcancel(title='Delete some Hosts',message='Hosts selected will be deleted, Are you sure?')
	    if anwser:
	        cursel.reverse()
	        for i in cursel:
		    tmp_name = self.listbox.get(i).strip('    |_')
		    p_pxe = Process(target=call, args=("rm -rf %s/%s" % (pxeconfigdir,manager_db.get_iphex_for_selected_host(tmp_name)),), kwargs={'shell': True})
		    p_dhcp = Process(target=manager_dhcp.delete_host_dhcp, args=(tmp_name,))
		    p_dns = Process(target=manager_dns.delete_host_dns, args=(tmp_name,))
		    p_inventory = Process(target=manager_inventory.delete_host_inventory, args=(tmp_name,))
		    p_db = Process(target=manager_db.delete_host_db, args=(tmp_name,))
		    for sp in p_pxe, p_dhcp, p_dns, p_inventory, p_db:
			sp.start()
		    for sp in p_pxe, p_dhcp, p_dns, p_inventory, p_db:
			sp.join()
		    if manager_zabbix:
		        manager_zabbix.delete_host_zabbix(tmp_name)
	            self.listbox.delete(i)
		if len(cursel) == 1:
	            showinfo(title='Delete host',message='The selected host is deleted')
		else:
	            showinfo(title='Delete some hosts',message='The selected hosts are deleted')

    def _add_host_dialog(self):
	self.entry_name.delete(0,END)
	self.entry_mac.delete(0,END)
	self.entry_macip.delete(0,END)
	self.entry_bmcip.delete(0,END)

    def _confirm(self):
	self.name = self.entry_name.get().strip()
	self.mac = self.entry_mac.get().strip().lower()
	self.macip = self.entry_macip.get().strip()
	self.bmcip = self.entry_bmcip.get().strip()

	self.pt = r'[0-9]+'

	if not self.name:
	    showerror(title='Error',message="Name can't be empty!")
	    return
	if not re.search(self.pt,self.name):
	    showerror(title='Error',message='At least a number in "name" field!')
	    return
	if not self.mac:
	    showerror(title='Error',message="Mac can't be empty!")
	    return
	if not self.macip:
	    showerror(title='Error',message="Macip can't be empty!")
	    return
	if not self.bmcip:
	    showerror(title='Error',message="BMCIP can't be empty!")
	    return
	if not manager_db.hostifexists_or_changeinfo(self.name,self.mac,self.macip,self.bmcip):
	    manager_db.add_host_db(self.name,self.mac,self.macip,self.bmcip)
	    manager_dhcp.add_host_dhcp(self.name,self.mac,self.macip)
	    manager_dns.add_host_dns(self.name,self.macip)
	    manager_inventory.add_host_inventory(self.name)
	    if manager_zabbix:
	        manager_zabbix.add_host_zabbix(self.name,self.macip)
            self.listbox.insert(END,"    |_%s" % self.name)
	    showinfo(title='Add Host',message='host add successfully')
	    return
	if manager_db.hostifexists_or_changeinfo(self.name,self.mac,
				      self.macip,self.bmcip) == "host exists":
	    showerror(title='Duplicate Host',message='Host Already Exists')
	    return

	self.name_changed = False
	for orign,dest in manager_db.hostifexists_or_changeinfo(self.name,self.mac,self.macip,self.bmcip)[::-1]:
	    if orign == manager_db.oldname:
		self.name_changed = True
		self.new_name = dest	
	    manager_db.replace_hostinfo_db(orign,dest)
	    manager_dhcp.replace_hostinfo_dhcp(manager_db.oldname,orign,dest)
	    manager_dns.replace_hostinfo_dns(manager_db.oldname,orign,dest)
	    manager_inventory.replace_hostinfo_inventory(manager_db.oldname,orign,dest)

	if self.name_changed:
	    for i in range(self.listbox.size()):
                if self.listbox.get(i).strip('    |_') == manager_db.oldname: 
		    self.listbox.delete(i)
		    self.listbox.insert(i,"    |_%s" % self.new_name)
        	    self.listbox.itemconfig(i,fg='black')
	            break
	else:
	    for i in range(self.listbox.size()):
                if self.listbox.get(i).strip('    |_') == manager_db.oldname: 
        	    self.listbox.itemconfig(i,fg='black')
	            break
	showinfo(title='Change Info',message='Change finished.')

    def _popup(self,event):
	curselection = list(self.listbox.curselection())
        if curselection == ['0'] and self.listbox.size() == 1:
	    self.popmenu2 = Menu(self.root, tearoff=0,bg='white',
				activebackground='orange')
	    self.popmenu2.add_command(label=' Refresh',
				      image=self.photo_refresh,
				      compound=LEFT,
				      command=self._refresh)
	    self.popmenu2.add_command(label=' New Host',accelerator='Ctrl+N',command=self._add_host_dialog,image=self.photo_nh,compound=LEFT)
	    self.popmenu2.post(event.x_root, event.y_root)
	    return
        if curselection == ['0']:
	    self.popmenu3 = Menu(self.root, tearoff=0,bg='white',
				activebackground='orange')
	    self.popmenu3.add_command(label=' Refresh',
				      image=self.photo_refresh,
				      compound=LEFT,
				      command=self._refresh)
	    self.popmenu3.add_command(label=' New Host',accelerator='Ctrl+N',command=self._add_host_dialog,image=self.photo_nh,compound=LEFT)
	    self.hostmenu = Menu(self.popmenu3,tearoff=0,bg='white',
				activebackground='orange')
	    self.hostmenu.add_command(label=' Power On',image=self.photo_poweron,compound=LEFT,command=lambda: self._poweron(curselection))
	    self.hostmenu.add_command(label=' Power Off',image=self.photo_poweroff,compound=LEFT,command=lambda: self._poweroff(curselection))
	    #self.hostmenu.add_command(label='Power Reset',command=lambda: self._powerreset(curselection))
	    self.hostmenu.add_command(label=' Install',image=self.photo_tm,compound=LEFT,command=lambda: self._install_system(curselection))
	    self.hostmenu.add_command(label=' Delete',image=self.photo_delete,compound=LEFT,command=self._delete_select)
	    self.popmenu3.add_cascade(label=' host',image=self.photo_right,compound=LEFT,menu=self.hostmenu)
	    self.popmenu3.post(event.x_root, event.y_root)
	    return
        if curselection == []:
	    return
        if '0' in curselection:
	    return
        if len(curselection) > 1:
	    self.popmenu4 = Menu(self.root, tearoff=0,bg='white',
				activebackground='orange')
	    self.popmenu4.add_command(label=' Refresh',
				      image=self.photo_refresh,
				      compound=LEFT,
				      command=self._refresh)
	    self.hostmenu = Menu(self.popmenu4,tearoff=0,bg='white',
				activebackground='orange')
	    self.hostmenu.add_command(label=' Power On',image=self.photo_poweron,compound=LEFT,command=lambda: self._poweron(curselection))
	    self.hostmenu.add_command(label=' Power Off',image=self.photo_poweroff,compound=LEFT,command=lambda: self._poweroff(curselection))
	    #self.hostmenu.add_command(label='Power Reset',command=lambda: self._powerreset(curselection))
	    self.hostmenu.add_command(label=' Install',image=self.photo_tm,compound=LEFT,command=lambda: self._install_system(curselection))
	    self.hostmenu.add_command(label=' Delete',image=self.photo_delete,compound=LEFT,command=self._delete_select)
	    self.popmenu4.add_cascade(label=' host',image=self.photo_right,compound=LEFT,menu=self.hostmenu)
	    self.popmenu4.post(event.x_root, event.y_root)
	    return
	self.popmenu = Menu(self.root, tearoff=0,bg='white',
			    activebackground='orange')
	self.popmenu.add_command(label=' Refresh',
				 image=self.photo_refresh,
				 compound=LEFT,
				 command=self._refresh)
	self.hostmenu = Menu(self.popmenu,tearoff=0,bg='white',
			    activebackground='orange')
	self.hostmenu.add_command(label=' Edit',
				  image=self.photo_edit,
				  compound=LEFT,
				  command=self._edit_host)
	self.hostmenu.add_command(label=' Power On',image=self.photo_poweron,compound=LEFT,command=lambda: self._poweron(curselection))
	self.hostmenu.add_command(label=' Power Off',image=self.photo_poweroff,compound=LEFT,command=lambda: self._poweroff(curselection))
	#self.hostmenu.add_command(label='Power Reset',command=lambda: self._powerreset(curselection))
	self.hostmenu.add_command(label=' Install',image=self.photo_tm,compound=LEFT,command=lambda: self._install_system(curselection))
	self.hostmenu.add_command(label=' Delete',image=self.photo_delete,compound=LEFT,command=self._delete_select)
	self.popmenu.add_cascade(label=' host',image=self.photo_right,compound=LEFT,menu=self.hostmenu)
	self.popmenu.post(event.x_root, event.y_root)

    def _refresh(self):
        pass

    def _edit_host(self):
	self._add_host_dialog()
	self.curselect_hostname = self.listbox.get(self.listbox.curselection()).strip('    |_')
	(name,mac,macip,bmcip) = manager_db.get_hostinfo_from_db(self.curselect_hostname)
	self.entry_name.delete(0,END)
	self.entry_name.insert(END,name) 
	self.entry_mac.delete(0,END)
	self.entry_mac.insert(END,mac) 
	self.entry_macip.delete(0,END)
	self.entry_macip.insert(END,macip) 
	self.entry_bmcip.delete(0,END)
	self.entry_bmcip.insert(END,bmcip) 

    def _invoke_add_host_dialog(self,event):
        self._add_host_dialog()

    def _invoke_reload(self,event):
        self._reload()

    def _import_host(self):
	try:
	    result,fn = cif.import_file()
	except TypeError:
	    return
        if result: 
	    if not self._append_import.get():
	        for i in manager_db.get_alliphexs_in_db():
	            call("rm -rf %s/%s" % (pxeconfigdir,i),shell=True)
	        manager_dhcp.delete_allhost_dhcp()
	        manager_dns.delete_allhost_dns()
	        manager_inventory.delete_allhost_inventory()
	        if manager_zabbix:
                    manager_zabbix.delete_allhost_zabbix()
                manager_db.delete_allhost_db()
		self.listbox.delete(1,END)
	    with open(fn) as fobj:
	        for line in fobj:
	            (name,mac,macip,bmcip) = line.split()
		    p_db = Process(target=manager_db.add_host_db, args=(name,mac.lower(),macip,bmcip))
		    p_dhcp = Process(target=manager_dhcp.add_host_dhcp, args=(name,mac.lower(),macip))
		    p_dns = Process(target=manager_dns.add_host_dns, args=(name,macip))
		    p_inventory = Process(target=manager_inventory.add_host_inventory, args=(name,))
		    for subpro in p_db, p_dhcp, p_dns, p_inventory:
			subpro.start()
		    for subpro in p_db, p_dhcp, p_dns, p_inventory:
			subpro.join()
	            if manager_zabbix:
	                manager_zabbix.add_host_zabbix(name,macip)
                    self.listbox.insert(END,"    |_%s" % name)
	    showinfo(title='Import',message='Import finished')

    def _invoke_import_host(self,event):
        self._import_host()

    def _ipmitool_base(self,title,message,ipmitool_func,action,cs):

	myq = Queue()
        subprocesses = []
	ipmitool_failed_hosts = []

	anwser = askokcancel(title=title,message=message)
	if anwser:
	    if ipmitool_func.__name__ == 'install_system':
	        if not self.ostype.get():
		    showerror('No ostype','Must select a "ostype"')
		    return
	    self.ot, self.otp = self._get_os_type_and_prefix()
	    if cs == ['0']:
		if ipmitool_func.__name__ == 'install_system':
		    for i in manager_db.get_alliphexs_in_db():
		        call("rm -rf %s/%s" % (pxeconfigdir,i),shell=True)
	        for name,bmcip in manager_db.get_all_hostname_bmcip_pairs():
		    subprocesses.append(Process(target=ipmitool_func,args=(name,bmcip,myq)))
	    else: 
	        for i in cs:
		    if ipmitool_func.__name__ == 'install_system':
			ht = manager_db.get_iphex_for_selected_host(self.listbox.get(i).strip('    |_'))
		        call("rm -rf %s/%s" % (pxeconfigdir,ht),shell=True)
	            name,bmcip = manager_db.get_hostname_bmcip_pairs(self.listbox.get(i).strip('    |_'))
		    subprocesses.append(Process(target=ipmitool_func,args=(name,bmcip,myq)))
	    if ipmitool_func.__name__ == 'install_system':
	        call("rm -rf %s/default" % pxeconfigdir, shell=True)
	        if self.otp == 'rhel' or self.otp == 'centos':
	            call("cp -a %s/default %s/default" % (tftp_rhel_config_dir,pxeconfigdir),shell=True)
	            call("rm -rf %s" % ks_file,shell=True)
		    if self._with_gui.get():
	                call("cp -a %s %s" % (ks_file_source_gui,ks_file),shell=True)
		    else:
	                call("cp -a %s %s" % (ks_file_source_text,ks_file),shell=True)
		    call("sed -i 's,#os_type#,%s,g' %s" % (self.ot,ks_file), shell=True)
		    call("sed -i 's,#os_type_prefix#,%s,g' %s" % (self.otp,ks_file), shell=True)
	        if self.otp == 'sles':
	            call("cp -a %s/default %s/default" % (tftp_sles_config_dir,pxeconfigdir),shell=True)
		call("sed -i 's,#os_type#,%s,g' %s/default" % (self.ot,pxeconfigdir), shell=True)
            for subprocess in subprocesses:
		subprocess.start()
            for subprocess in subprocesses:
		subprocess.join()

	    while not myq.empty():
		ipmitool_failed_hosts.append(myq.get())
	    
	    if ipmitool_failed_hosts:
		showerror(title='%s failed' % action,message='%s %s failed' % (sorted(ipmitool_failed_hosts), action))
	    else:
		showinfo(title='success',message='%s successfully' % action)

    def _message_base(self,m,cs):
	if cs == ['0']:
            message='All hosts will "%s", Are you sure?' % m
	elif len(cs) == 1:
            message='Host selected will "%s", Are you sure?' % m
	else:
            message='Hosts selected will "%s", Are you sure?' % m
	return message

    def _install_system(self,cs):
	self._ipmitool_base('Install System',self._message_base("reinstall",cs),manager_install.install_system,'Install',cs)

    def _poweron(self,cs):
        self._ipmitool_base('Power On',self._message_base("power on",cs),manager_install.poweron,'PowerOn',cs)

    def _poweroff(self,cs):
        self._ipmitool_base('Power Off',self._message_base("power off",cs),manager_install.poweroff,'PowerOff',cs)

    def _powerreset(self,cs):
        self._ipmitool_base('Power Reset',self._message_base("power reset",cs),manager_install.powerreset,'PowerReset',cs)

    def _reload(self):
	(output_dhcp, exit_dhcp) = run(restart_dhcp, withexitstatus=True)
        if exit_dhcp != 0:
            showerror(title='Reload Error',message='dhcp reload failed!')
	    return
	(output_dns, exit_dns) = run(restart_dns, withexitstatus=True)
        if exit_dns != 0:
            showerror(title='Reload Error',message='dns reload failed!')
	    return
	showinfo(title='Reload Success',message='reload successfully.')

    def _select_configfile(self):
	os.chdir(web_root_dir)
	filename = askopenfilename(filetypes=[('AutoCF','.xml')])
	if filename:
	    call('ln -sf %s AutoConfigFile' % filename, shell=True)

    def _set_item_color(self):
        size = self.listbox.size()
        if size == 1:
	    pass
        else:
	    myq = Queue()
	    subps = []
	    index_state_pairs = []
	    for i in range(1, size):
	        NAME = self.listbox.get(i).strip('    |_')
	        subps.append(Process(target=manager_state.get_host_index_state_pair,args=(NAME,i,myq)))
	    for subp in subps:
	        subp.start()
	    for subp in subps:
	        subp.join()

	    while not myq.empty():
		index_state_pairs.append(myq.get())

	    for index,state in index_state_pairs:
	        if state == 'on':
		    self.listbox.itemconfig(index,fg='green')
	        elif state == 'off':
		    self.listbox.itemconfig(index,fg='red')
                elif state == 'unknown':
		    self.listbox.itemconfig(index,fg='blue')
        self.listbox.after(120000, self._set_item_color)
    
    def _get_os_type_and_prefix(self):
	ot = self.ostype.get()
        try:
	    otp = re.match(r'[a-zA-Z]+',ot).group().lower()
	except AttributeError:
	    otp = 'sles'
	    ot = 'sles11sp4'
	if otp not in ('sles','rhel','centos'):
	    otp = 'sles'
	    ot = 'sles11sp4'
	return ot, otp

    def _display_cursel_host_info(self,event):
	if self.listbox.curselection() == ('0',):
	    return
	cshn = self.listbox.get(self.listbox.curselection()).strip('    |_')
	(fir_name,fir_mac,fir_macip,fir_bmcip) = Popen(["grep", cshn,db_file], stdout=PIPE).communicate()[0].split()
	self._add_host_dialog()
        self.entry_name.insert(END,fir_name)
        self.entry_mac.insert(END,fir_mac)
        self.entry_macip.insert(END,fir_macip)
        self.entry_bmcip.insert(END,fir_bmcip)

    def _notice_to_select_autoxmlfile(self,event):
	ot, otp = self._get_os_type_and_prefix()
	if otp == 'sles':
	    self.ckb_with_gui_or_not.forget()
	    showinfo('select autoxml file', 
		     'Click the button "AutoXML" bellow to select a "autoxml file" in "%s" for "%s"' % (web_root_dir, ot))
	elif otp == 'rhel' or otp == 'centos':
	   self.ckb_with_gui_or_not.pack(side=LEFT)

    def _edit_authentication(self):
	self.tl = Toplevel(self.root)
	self.tl.title('Runner Authentication')
	self.tl.geometry('+%s+%s' % ((self.x + 50), (self.y + 150)))
	self.tl.resizable(0,0)
	self.fm_remote_user = Frame(self.tl)
	self.fm_remote_user.pack(fill=X,pady=5)
	self.fm_save_auth = Frame(self.tl)
	self.fm_save_auth.pack(fill=X,pady=5)
	self.lb_remote_user = Label(self.fm_remote_user,text='remote_user: ')
	self.lb_remote_user.pack(side=LEFT)
	self.entry_remote_user = Entry(self.fm_remote_user, width=10)
	self.entry_remote_user.pack(side=LEFT)
	self.lb_user_password = Label(self.fm_remote_user,text='user_password: ')
	self.lb_user_password.pack(side=LEFT)
	self.entry_user_password = Entry(self.fm_remote_user,show="*",width=15)
	self.entry_user_password.pack(side=LEFT)
	self.bt_passwd_visible = Checkbutton(self.fm_save_auth,text='Visible',onvalue=1,variable=self._passwd_visible, command=self._set_passwd_visible_or_not) 
	self.bt_save_auth = Button(self.fm_save_auth,text='Save',command=self._save_not_exit)
	self.bt_exit_auth = Button(self.fm_save_auth,text='Exit',command=lambda : self.tl.destroy())
	self.bt_exit_auth.pack(side=RIGHT)
	self.bt_save_auth.pack(side=RIGHT,padx=10)
	self.bt_passwd_visible.pack(side=RIGHT, padx=20)

	self._ru, self._rup = manager_auth.get_user_passwd_for_runner()
	self.entry_remote_user.insert(0,self._ru)
	self.entry_user_password.insert(0,self._rup)
	
	self.entry_remote_user.bind('<Control-u>', lambda event: self.entry_remote_user.delete(0,END))
	self.entry_remote_user.bind('<Control-U>', lambda event: self.entry_remote_user.delete(0,END))
	self.entry_user_password.bind('<Control-u>', lambda event: self.entry_user_password.delete(0,END))
	self.entry_user_password.bind('<Control-U>', lambda event: self.entry_user_password.delete(0,END))

    def _set_passwd_visible_or_not(self):
	if self._passwd_visible.get():
	    self.entry_user_password.config(show='')
	else:
	    self.entry_user_password.config(show='*')

    def _save_not_exit(self):
	self._remote_user = self.entry_remote_user.get().strip()
	if not self._remote_user:
	    showerror('no user', '"user" can not be empty!')
	    return
	self._user_password = self.entry_user_password.get().strip()
	if not self._user_password:
	    showerror('no password', '"password" can not be empty!')
	    return
	manager_auth.set_user_passwd_for_runner(self._remote_user,self._user_password)

    def _add_another_widget_or_not(self,event):
	smn = self.module_name.get()
	if smn == 'ping':
	    self.fm_shell_commands.forget()
	    self.fm_copy_args.forget()
	elif smn == 'shell':
	    self.fm_copy_args.forget()
	    self.fm_shell_commands.pack(fill=X)
	elif smn == 'copy':
	    self.fm_shell_commands.forget()
	    self.fm_copy_args.pack(fill=X)

    def _run_action(self):
	select_hosts, runner_inventory_hosts, use_tmp = self._get_current_select_hostnames()
	if select_hosts == 'invalid': return
	if select_hosts == 'no_host': return
	if not select_hosts:
	    showerror('no host select','At least one host should be selected to run')
	    return
	select_module_name = self.module_name.get()
	ru, rup = manager_auth.get_user_passwd_for_runner()
	if select_hosts == 'all' and use_tmp:
	    host_count = int(Popen('wc -l < %s' % runner_tmp_inventory_hosts, shell=True, stdout=PIPE).communicate()[0].strip())
	    if host_count >= 2:
                anwser = askokcancel(title='begin run',message='keeped hosts will be run, are you sure?')
	    else:
                anwser = askokcancel(title='begin run',message='keeped host will be run, are you sure?')
	elif select_hosts == 'all':
            anwser = askokcancel(title='begin run',message='"all" hosts will be run, are you sure?')
	elif len(select_hosts) == 1:	
            anwser = askokcancel(title='begin run',message='select host will be run, are you sure?')
	else:
            anwser = askokcancel(title='begin run',message='select hosts will be run, are you sure?')
	if anwser:
	    if select_hosts != 'all':
	        if len(select_hosts) == 1:
		    select_hosts = ''.join(select_hosts)+".ma"
		else:
		    select_hosts = [ host+'.ma' for host in select_hosts ]
		    select_hosts = ':'.join(select_hosts)
	    self.listbox_in_tab2.delete(0,END)
	    if select_module_name == 'ping':
		self._run_action_base('ansible -i %s "%s" -m ping -e "ansible_ssh_user=%s ansible_ssh_pass=%s"' % (runner_inventory_hosts, select_hosts, ru, rup))
	    elif select_module_name == 'shell':
		run_cmd = self.entry_shell_commands.get().strip()
		if not run_cmd:
		    showerror('no commands', '"Commands" can not be empty')
		    return
		self._run_action_base('ansible -i %s "%s" -m shell -a """%s""" -e "ansible_ssh_user=%s ansible_ssh_pass=%s"' % (runner_inventory_hosts, select_hosts, run_cmd, ru, rup))
	    elif select_module_name == 'copy':
		mylocal = self.entry_copy_local.get().strip()
		if not mylocal:
		    showerror('no local', '"Local" cat not be empty')
		    return
		mydest = self.entry_copy_dest.get().strip()
		if not mydest:
		    showerror('no dest', '"Dest" cat not be empty')
		    return
		if os.path.isdir(mylocal):
		    if not os.path.isdir(mydest):
			showerror('Different Type', '"Dest" must also be a directory.')
			return
		self._run_action_base('ansible -i %s "%s" -m copy -a """src=%s dest=%s""" -e "ansible_ssh_user=%s ansible_ssh_pass=%s"' % (runner_inventory_hosts, select_hosts, mylocal, mydest, ru, rup))

    def _run_action_base(self, your_cmd):
	#print your_cmd
	i = 0
	for line in Popen(your_cmd,shell=True, stdout=PIPE,stderr=STDOUT).stdout:
            self.listbox_in_tab2.insert(END,line.strip())
            if "Error" in line or "FAILED" in line or "UNREACHABLE" in line:
                self.listbox_in_tab2.itemconfig(i,bg='red')
            elif "SUCCESS" in line:
                self.listbox_in_tab2.itemconfig(i,bg='green')
            self.root.update()
            i+= 1
	showinfo('run done', 'For details see "Results"')

    def _get_current_select_hostnames(self):
	tmp_inventory = runner_inventory_hosts
	use_tmp = False
	select_hosts = 'all'
	if self._keeped_host.get() == 1:
	    tmp_inventory = runner_tmp_inventory_hosts
	    use_tmp = True
	    return select_hosts, tmp_inventory, use_tmp
        mycs = self.listbox.curselection()
        if not mycs: 
	    select_hosts = []
        elif len(mycs) > 1 and '0' in mycs:
            showerror('select error','''"Computers" and hosts can't be selected at the same time''')
            select_hosts = 'invalid'
	elif mycs == ('0',) and self.listbox.size() == 1:
	    showerror('no avaliable host','''no available host to run''')
	    select_hosts = 'no_host'
        elif mycs == ('0',):
	    pass
	else:
	    select_hosts = []
            for i in mycs:
                select_hosts.append(self.listbox.get(i).strip('    |_'))
        return select_hosts, tmp_inventory, use_tmp

    def _about_cluster_manager(self):
	self.tp_about = Toplevel(self.root)
	self.tp_about.title('Cluster Manager')
	self.tp_about.geometry('+%s+%s' % ((self.x + 50), (self.y + 150)))
        self.tp_about.resizable(0,0)
	text_about = Text(self.tp_about,width=34, height=4, bg='gray')
        text_about.pack()

	text_about.tag_configure('big', font=('Verdana', 10, 'bold'))
	text_about.insert(END,'''               version: 3.0\n''', 'big')
	text_about.insert(END,'\n')
	text_about.insert(END,'  Support OS: sles, rhel, centos  ')
	text_about.config(state='disabled')

    def _show_keeped_hosts(self):
	self.tp_show_keeped_hosts = Toplevel(self.root)
	self.tp_show_keeped_hosts.title('result')
        self.tp_show_keeped_hosts.geometry('180x200+%s+%s' % ((self.x + 180), (self.y + 150)))
        self.tp_show_keeped_hosts.resizable(0,0)
	self.listbox_show_keeped_hosts = Listbox(self.tp_show_keeped_hosts)
	self.listbox_show_keeped_hosts.pack(side=LEFT,fill=BOTH,expand=True)
	self.sb_show_keeped_hosts = Scrollbar(self.tp_show_keeped_hosts,orient=VERTICAL)
	self.sb_show_keeped_hosts.pack(side=LEFT,fill=Y)
	self.sb_show_keeped_hosts.config(command=self.listbox_show_keeped_hosts.yview)
	self.listbox_show_keeped_hosts.config(yscrollcommand=self.sb_show_keeped_hosts.set)
	self.listbox_show_keeped_hosts.delete(0,END)
	try:
	    with open(runner_tmp_inventory_hosts) as myobj:
	        for i in myobj:
	            self.listbox_show_keeped_hosts.insert(END,i.strip().strip('.ma'))
	except IOError:
	    pass

    def _do_keep_host(self):
	if self._keeped_host.get():
	    mycs = self.listbox.curselection()
	    mysize = self.listbox.size()
	    if mysize == 1:
                showerror('no avaliable host','''no available host to keep''')
		self.cbt_keeped_hosts.deselect()
            elif not mycs:
	        showerror('no host select', 'At least one host should be selected to keep.')
		self.cbt_keeped_hosts.deselect()
            elif len(mycs) > 1 and '0' in mycs:
                showerror('select error','''"Computers" and hosts can't be selected at the same time''')
		self.cbt_keeped_hosts.deselect()
            else:
		if mycs == ('0',):
	            call('cp %s %s' % (runner_inventory_hosts, runner_tmp_inventory_hosts), shell=True)
	            call("sed -i '/^#/d' %s" % runner_tmp_inventory_hosts, shell=True)
		else:
                    call('touch %s' % runner_tmp_inventory_hosts, shell=True)
                    with open(runner_tmp_inventory_hosts,'w') as fobj_tmp_hosts:
                        for i in mycs:
                            fobj_tmp_hosts.write(self.listbox.get(i).strip('    |_') + '.ma' + '\n')
		if len(mycs) > 1 or (mysize >=3 and mycs == ('0',)):
		    self.bt_show_keeped_hosts.config(text='show keeped hosts')
		else:
		    self.bt_show_keeped_hosts.config(text='show keeped host')
	        self.bt_show_keeped_hosts.pack(side=RIGHT,pady=3,padx=3)
        else:
	    call('rm -rf %s' % runner_tmp_inventory_hosts, shell=True)
	    self.bt_show_keeped_hosts.forget()
    
class validate(object):
    def __init__(self,width=350,height=180):
        self.root = Tk()
	self.root.title('cluster manager login')
	self.width = width
	self.height = height
        self.screen_width=self.root.winfo_screenwidth()
	self.screen_height=self.root.winfo_screenheight()
	self.x = ((self.screen_width - self.width) / 2)
	self.y = ((self.screen_height - self.height) / 2)
        self.root.geometry('%sx%s+%s+%s' % (self.width,self.height,self.x,self.y))
        self.root.resizable(False, False)

	self.ft_cluster = Font(size=20,weight='bold')
	self.ft_user = Font(size=15)
	self.ft_password = Font(size=15)
	self.ft_entry = Font(size=15)
	self.ft_confirm = Font(size=10,weight='bold')
	self.ft_quit = Font(size=10,weight='bold')

	#### define widgets ###
	self.fm_cluster = Frame(self.root)
	self.lb_cluster = Label(self.fm_cluster,
				font = self.ft_cluster,
				text='Cluster Manager',fg='purple')
	self.lb_cluster.pack()
	self.fm_cluster.pack(expand=True)

	self.fm_user = Frame(self.root)
	self.lb_user = Label(self.fm_user,text='User: ',
			     font=self.ft_user,fg='orange',width=8)
	self.lb_user.pack(side=LEFT)
	self.en_user = Entry(self.fm_user,font=self.ft_entry,width=12)
	self.en_user.pack(side=LEFT)
	self.fm_user.pack()

	self.fm_password = Frame(self.root)
	self.lb_password = Label(self.fm_password,text='Password: ',
			     font=self.ft_password,fg='orange',width=8)
	self.lb_password.pack(side=LEFT)
	self.en_password = Entry(self.fm_password,show="*",
				font=self.ft_entry,
				width=12)
	self.en_password.pack(side=LEFT)
	self.fm_password.pack()
	self.fm_con_quit = Frame(self.root)
	self.bt_quit = Button(self.fm_con_quit,text='Quit',
			     background='red',activebackground='red',
			     underline='0',
			     command=self.root.destroy,font=self.ft_quit)
	self.bt_quit.pack(side=RIGHT)
	self.bt_confirm = Button(self.fm_con_quit,
				text='Confirm',
				background='green',
				activebackground='green',
				underline='0',
			        command=self._confirm,
				font=self.ft_confirm)
	self.bt_confirm.pack(side=LEFT,padx=15)
	self.fm_con_quit.pack(fill=X,pady=15,padx=60)

        #### end define ########

	self.root.bind('<Return>',lambda event: self._confirm())
	self.root.mainloop()

    def _confirm(self):
	user = self.en_user.get().strip()
	password = self.en_password.get().strip()
	if not user:
	    showwarning(title='no user',message='please enter a user')
	elif not password:
	    showwarning(title='no password',message='please enter password')
	elif user == 'root' and password == 'root':
	    self.root.destroy()
            hpc = Sgishsc()
	    hpc.root.mainloop()
	else:
	    showerror(title='Auth Failure',message='Login failed')

if __name__ == "__main__":
    validate()

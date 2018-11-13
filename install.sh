#!/bin/bash

# Source function library
topdir=$(cd `dirname $0`; pwd)
. ${topdir}/localrc

echo "installation starting ..."
##################################
# install and config dhcp server #
##################################
# phase1 install
install_pkg "installing dhcp server " $dhcp_server_pname
install_pkg "installing syslinux  " syslinux
# phase2 config
echo "configing dhcp server ..."
while [ "$interface" = '' ]
do
    echo -ne "\033[40;37m1.\033[0m interface that dhcp will listen on [eg: eth0|ens33 ...]: "
    read interface 
done

ip_interface=$(ip a |grep $interface |grep inet | awk '{print $2}' | awk -F"/" '{print $1}')
if [ "$ip_interface" = '' ]; then
    echo -e "\033[31minvalid interface: $interface\033[0m"
    exit 1
fi

while [ "$subnet" = '' ]
do
    echo -ne "\033[40;37m2.\033[0m Enter a subnet: "
    read subnet
done
while [ "$netmask" = '' ]
do
    echo -ne "\033[40;37m3.\033[0m Enter a netmask: "
    read netmask
done

[ -f ${dhcp_configure_file}.bak ] || cp $dhcp_configure_file ${dhcp_configure_file}.bak

cat > $dhcp_configure_file <<EOF
#==================================#
#    DO NOT MODIFY THIS SECTION    #
#==================================#
ddns-update-style none;
default-lease-time -1;
max-lease-time -1;
next-server $ip_interface;
filename "pxelinux.0";

subnet $subnet netmask $netmask {
}

group "cluster" {
}
EOF

if ! grep -q $interface $dhcp_systemd_file; then
    sed -i '/ExecStart/a\'$interface'' $dhcp_systemd_file
    sed -i '/ExecStart/N; {s/\n/ /}' $dhcp_systemd_file
fi

echo_done "configing dhcp server "
start_and_enable_server "starting dhcp server " $dhcp_systemd_name
#######################################
#   install and config dns server     #
#######################################
install_pkg "installing bind server " $bind_server_pname
echo "configuring bind server ..."
if ! grep -q -x 'zone "ma" in {' $bind_configure_file; then
cat >> $bind_configure_file << EOF
zone "ma" in {
	allow-transfer { none; };
	file "ma";
	type master;
};
EOF
fi

cat > ${bind_work_dir}/ma << EOF
\$TTL 2d
@		IN SOA		admin.ma.	root (
				000001		; serial
				3h		; refresh
				1h		; retry
				1w		; expiry
				1d )		; minimum

		IN NS		admin.ma.
admin		IN A		$ip_interface
EOF

sed -i 's/::1/none/' $bind_configure_file
if ! grep -q "\-4" $bind_systemd_file; then
    sed -i '/ExecStart/a\-4' $bind_systemd_file
    sed -i '/ExecStart/N; {s/\n/ /}' $bind_systemd_file
fi
sed -i '/^[^#]/d' /etc/resolv.conf
echo "nameserver 127.0.0.1" >> /etc/resolv.conf

echo_done "configing bind server "
start_and_enable_server "starting bind server " $bind_systemd_name
##################################
# install and config tftp server #
##################################
# phase1 install
install_pkg "installing tftp server " "$tftp_server_pname"
# phase2 config
echo "configing tftp server ..."

if [ ! -d $tftp_root_dir ]; then
    mkdir -p $tftp_root_dir
fi

rm -rf $tftp_root_dir/*
cp -r $rp/tftp/tftpboot_contents/* $tftp_root_dir/
rm -rf $basedir
mkdir -p $basedir
cp -r $rp/tftp/tftp_opt_sgishsc $basedir/tftp
for i in rhel sles
do
    sed -i 's,%address%,'$ip_interface',g' $basedir/tftp/$i/default
done
### get sles11sp4 boot files ######################
#while [ "$sles11sp4" = '' ]
#do
#    echo -ne "\033[40;37m4.\033[0m specify the sles11sp4 mount point: "
#    read sles11sp4
#done
#sles11sp4=$(expr match "$sles11sp4" '.*\(^/.*[^/]\)')
#if ! cp $sles11sp4/boot/x86_64/loader/linux $tftp_root_dir/sles/linux_sles11sp4 &>/dev/null; then
#    echo -e "\033[31m[Error]: can not get kernel file for sles11sp4. check the mount point and try again.\033[0m"
#    exit 1
#fi
#cp $sles11sp4/boot/x86_64/loader/initrd $tftp_root_dir/sles/initrd_sles11sp4
#################################################################################
sed -i '/disable/d' /etc/xinetd.d/tftp
chown root.root $tftp_root_dir
chmod 755 $tftp_root_dir

echo_done "configing tftp server "
start_and_enable_server "starting tftp server " $tftp_systemd_name
####################################
# install and config web server    #
####################################
# phase1 install
install_pkg "installing web server " $web_server_pname
# phase2 config
echo "configing web server ..."

# for rhel7
sed -i 's/#ServerName www.example.com:80/ServerName www.example.com:80/' $web_configure_file
for i in httpd-default.conf httpd-languages.conf httpd-mpm.conf httpd-multilang-errordoc.conf
do
    scp /usr/share/doc/httpd-2.4.6/$i $web_configure_dir/
done
#######
cat > $web_configure_dir/httpd-mpm.conf <<EOF
PidFile "/run/httpd/httpd.pid"
<IfModule mpm_prefork_module>
    ServerLimit		     500
    StartServers             8
    MinSpareServers          8
    MaxSpareServers          16
    MaxRequestWorkers        500
    MaxConnectionsPerChild   4000
</IfModule>
<IfModule !mpm_netware_module>
    MaxMemFree            2048
</IfModule>
<IfModule mpm_netware_module>
    MaxMemFree             100
</IfModule>
EOF

[ -d $web_root_dir ] || mkdir -p $web_root_dir
#rm -rf $web_root_dir/*
[ -d $web_root_dir/tools ] || mkdir $web_root_dir/tools
for j in ks
do
[ -d ${web_root_dir}/$j ] || mkdir ${web_root_dir}/$j
done
scp $rp/autoinst_tools/ftp $web_root_dir/tools/
cp -r $rp/ks $basedir/
for i in `ls $basedir/ks/*.cfg`
do
    sed -i 's,%address%,'$ip_interface',g' $i
done
ln -sf $basedir/ks/rhel7_gui.cfg $basedir/ks/rhel_gui.cfg
ln -sf $basedir/ks/rhel7_text.cfg $basedir/ks/rhel_text.cfg
chmod 755 $web_root_dir/tools/ftp 

echo_done "configing web server "
start_and_enable_server "starting web server " $web_systemd_name
####################################
#       install vsftpd server      #
####################################

install_pkg "installing ftp server " $ftp_server_pname

echo "Configuring ftp server ..."
[ ! -f ${ftp_configure_file}.bak ] && cp $ftp_configure_file ${ftp_configure_file}.bak
cat > $ftp_configure_file << EOF
anonymous_enable=YES
local_enable=NO
local_umask=022
dirmessage_enable=YES
connect_from_port_20=YES
#xferlog_enable=YES
xferlog_std_format=NO
listen=YES
listen_ipv6=NO
pam_service_name=vsftpd
userlist_enable=YES
tcp_wrappers=YES

anon_root=/var/lib/tftpboot
anon_umask=022
write_enable=YES
anon_upload_enable=YES
anon_mkdir_write_enable=YES
anon_other_write_enable=YES
EOF

chown ftp:root $tftp_root_dir/pxelinux.cfg
[ -d $autoinst_tools_dir ] || mkdir -p $autoinst_tools_dir
rm -rf $autoinst_tools_dir/*
cp $rp/autoinst_tools/* $autoinst_tools_dir/
for i in `ls $autoinst_tools_dir/*.sh`
do
    sed -i 's,%address%,'$ip_interface',g' $i
done

echo_done "configing ftp server "
start_and_enable_server "starting ftp server " $ftp_systemd_name
####################################
#       install cluster manager        #
####################################
echo "installing cluster manager ..."
if ! python -c "import ttk" &>/dev/null; then
    echo "installing tkinter ..."
    $pm $rp/NotLocalRepo/tkinter/* >/dev/null
fi

if ! which ipmitool &>/dev/null; then
    install_pkg "installing ipmitool " ipmitool
fi
if ! python -c "from PIL import Image" &>/dev/null; then
    install_pkg "installing python-pillow " python-pillow
fi

if ! python -c "from PIL import ImageTk" &>/dev/null; then
    echo "installing python-pillow-tk ..."
    $pm $rp/NotLocalRepo/python-pil-tk/*
fi

[ -d ${cluster_configure_dir} ] || mkdir -p ${cluster_configure_dir}
rm -rf ${cluster_configure_dir}/*
cp $rp/crm/crm.conf ${cluster_configure_dir}/
cp -r $rp/crm/crm_need_dirs/* $basedir/

rm -rf /usr/lib64/python2.7/site-packages/sgishsc
cp -r $rp/crm/sgishsc /usr/lib64/python2.7/site-packages/

if ! python -c "import pexpect" &>/dev/null; then
    install_pkg "installing pexpect " pexpect
fi

cat > /root/Desktop/ClusterManager.desktop <<EOF
#!/usr/bin/env xdg-open

[Desktop Entry]
Encoding=UTF-8
Version=1.0
Type=Application
Terminal=false
Icon[en_US]=gnome-panel-launcher
Name[en_US]=Cluster Manager
Exec=python ${bindir}/hpcli.py
Name=Cluster Manager
Icon=${imagedir}/dsk.png
EOF

chmod +x /root/Desktop/ClusterManager.desktop

echo_done "installing cluster manager "

passwd=11111111

install_pkg "installing expect " expect

expect <<-EOF
    spawn vncpasswd /.passwd
    expect "Password:" { send "${passwd}\r" }
    expect "Verify:" { send "${passwd}\r" }
    expect "password (y/n)?" { send "n\r" }
    expect eof
EOF

install_pkg "installing nmap " nmap
install_pkg "installing tigervnc " tigervnc

scp $rp/cluster-commands/cluster-mip /usr/sbin/
chmod 755 /usr/sbin/cluster-mip
##########################################
systemctl stop firewalld &>/dev/null
systemctl disable firewalld &>/dev/null
##########################################
# install pyzabbix
install_pkg "installing python-setuptools " python-setuptools
tar xf $rp/zabbix/pyzabbix-0.7.4.tar.gz
cd pyzabbix-0.7.4
python setup.py install &>/dev/null
cd ../
rm -rf pyzabbix-0.7.4
############################################
tar xf $rp/zabbix/zabbix-api-0.5.3.tar.gz
cd zabbix-api-0.5.3
python setup.py install &>/dev/null
cd ../
rm -rf zabbix-api-0.5.3
############################################
chmod +x /root/Desktop/ClusterManager.desktop
#===========================================
if ! which ansible &>/dev/null; then
    echo "installing ansible ..."
    if ! $pm $rp/ansible/* >/dev/null; then
        echo -e "\033[31m[Error]: install ansible failed.\033[0m"
        exit 1
    fi
    echo "configuring ansible ..."
[ ! -e ${ansible_configure_file}.bak ] && cp $ansible_configure_file ${ansible_configure_file}.bak
cat > /etc/ansible/ansible.cfg <<EOF
[defaults]
forks          = 500
host_key_checking = False
retry_files_save_path = ~/.ansible-retry
command_warnings = False
[privilege_escalation]
[paramiko_connection]
record_host_keys=False
[ssh_connection]
pipelining = True
[persistent_connection]
connect_timeout = 30
connect_retries = 30
connect_interval = 1
[accelerate]
[selinux]
[colors]
[diff]
EOF
# test ansible
echo_done "ansible install and config "
else
[ ! -e ${ansible_configure_file}.bak ] && cp $ansible_configure_file ${ansible_configure_file}.bak
cat > /etc/ansible/ansible.cfg <<EOF
[defaults]
forks          = 500
host_key_checking = False
retry_files_save_path = ~/.ansible-retry
command_warnings = False
[paramiko_connection]
record_host_keys=False
[ssh_connection]
pipelining = True
[persistent_connection]
connect_timeout = 30
connect_retries = 30
connect_interval = 1
EOF
    echo_done "ansible config "
fi

echo
echo -e "\033[32minstallation finished.\033[0m"
echo

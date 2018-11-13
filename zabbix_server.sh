#!/bin/bash

# Source function library
rootdir=$(cd `dirname $0`; pwd)
. ${rootdir}/localrc

echo "install staring ..."
# install php packages
echo "installing php packages for zabbix_server ..."
$pm $rp/NotLocalRepo/php/*.rpm >/dev/null
# install zabbix server
$pm $rp/zabbix/*.rpm >/dev/null
# install mariadb
install_pkg "installing mariadb " ${mariadb_pname}
start_and_enable_server "starting mariadb " $mariadb_systemd_name

echo "creating db for zabbix_server ..."
mysql -uroot -e "drop database if exists zabbix"
mysql -uroot -e "create database zabbix character set utf8 collate utf8_bin;"
mysql -uroot -e "grant all privileges on zabbix.* to 'zabbix'@'localhost' identified by 'zabbix';"
mysql -uroot -e "flush privileges"
echo "creating table for zabbix_server ..."
for table in schema.sql images.sql data.sql
do
    mysql -uzabbix -pzabbix zabbix < /usr/share/doc/zabbix-server-mysql-2.2.19/create/$table
done

echo "configuring zabbix_server ..."
[ -e ${zabbix_server_configure_file}.bak ] ||  cp ${zabbix_server_configure_file} ${zabbix_server_configure_file}.bak
cat > ${zabbix_server_configure_file} << EOF
LogFile=/var/log/zabbix/zabbix_server.log
LogFileSize=0
PidFile=/var/run/zabbix/zabbix_server.pid
DBName=$db_name
DBUser=$db_user
DBPassword=$db_passwd
DBSocket=/var/lib/mysql/mysql.sock
SNMPTrapperFile=/var/log/snmptt/snmptt.log
CacheSize=256M
AlertScriptsPath=/usr/lib/zabbix/alertscripts
ExternalScripts=/usr/lib/zabbix/externalscripts
FpingLocation=$fping_file
EOF
chown root:zabbix $fping_file
chmod 4710 $fping_file
[ ! -e ${zabbix_reinstall_php_file}.bak ] && cp $zabbix_reinstall_php_file ${zabbix_reinstall_php_file}.bak
scp $rp/zabbix/menu.inc.php ${zabbix_reinstall_php_dir}/

scp $rp/zabbix/zabbix.conf.php ${zabbix_server_php_configure_file}/
chown apache.apache ${zabbix_server_php_configure_file}/zabbix.conf.php

echo_done "configing zabbix_server "
start_and_enable_server "starting zabbix_server " $zabbix_server_systemd_name

echo "configure and restarting httpd ..."
if ! grep -q Rewrite $web_configure_file; then
cat >> $web_configure_file <<EOF

RewriteEngine on
RewriteRule "^/\$" "/zabbix/index.php" [R]
EOF
fi
sed -i '/date.timezone/c\\tphp_value date.timezone Asia/Shanghai' ${web_configure_dir}/zabbix.conf
systemctl restart $web_systemd_name
echo_done "configure and restarting httpd "

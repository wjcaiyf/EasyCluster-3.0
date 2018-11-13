#!/bin/bash
wget -q http://%address%/tools/ftp -O /usr/bin/ftp
chmod 755 /usr/bin/ftp

ip=$(ifconfig eth0 |grep -w inet |awk '{print $2}'| cut -d: -f2)
ip_hex=$(gethostip ${ip} | awk '{print $3}')

cat > /tmp/${ip_hex} << EOF
default harddisk

# hard disk
label harddisk
  localboot 0x80
EOF

cd /tmp
ftp -n << EOF
open %address%
user ftp ftp
cd pxelinux.cfg
delete ${ip_hex}
put ${ip_hex}
bye
EOF

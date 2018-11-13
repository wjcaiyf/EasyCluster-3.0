first_dev=$(ip link | grep "^2:" | awk '{ print $2}' | cut -d':' -f1)
ip=$(ifconfig ${first_dev} |grep -w inet |awk '{print $2}' | cut -d":" -f2)
ip_hex=$(gethostip ${ip} | awk '{print $3}')

cat > /tmp/${ip_hex} << EOF
default harddisk

# hard disk
label harddisk
  localboot 0x80
EOF

cd /tmp
ftp -n << EOF
open $admin_host
user ftp ftp
cd pxelinux.cfg
delete ${ip_hex}
put ${ip_hex}
bye
EOF

#===============set ip for second interface ===================
netmask=16
#dgw=10.122.22.1
#set_ib_ip=yes
ib_interface_number=4
netmask_ib=16
#==============================================================

myhostname=`cat /tmp/hostname.txt`

ip_sec=$(grep ${myhostname}$ /etc/hosts | awk '{ print $1}')

second_interface=$(ip link |grep "^3:" | awk '{ print $2}' | cut -d':' -f1)
cn=$(nmcli -f connection.id c show $second_interface | awk '{ print $2}')

if [ -z "${dgw:-}" ]; then
    nmcli c modify $cn ipv4.method manual ipv4.addresses ${ip_sec}/${netmask}
else
    nmcli c modify $cn ipv4.method manual ipv4.addresses ${ip_sec}/${netmask} ipv4.gateway $dgw
fi

hostnamectl set-hostname $myhostname

nmcli c down $cn
sleep 1
nmcli c up $cn
nmcli c modify $cn connection.autoconnect yes

if [ ! -z "${set_ib_ip:-}" ]; then
    ip_ib=$(grep ${myhostname}-ib /etc/hosts | awk '{ print $1}')
    interface_ib=$(ip link |grep "^${ib_interface_number}:" | awk '{ print $2}' | cut -d':' -f1)
    cn_ib=$(nmcli -f connection.id c show $interface_ib | awk '{ print $2}')
    nmcli c modify $cn_ib ipv4.method manual ipv4.addresses ${ip_ib}/${netmask_ib}
    nmcli c down $cn_ib
    sleep 1
    nmcli c up $cn_ib
    nmcli c modify $cn_ib connection.autoconnect yes
fi

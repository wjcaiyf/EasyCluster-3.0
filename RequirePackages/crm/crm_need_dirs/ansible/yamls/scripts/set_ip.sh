#!/bin/bash

rm -rf /root/.ssh

[ $# -ne 2 ] && echo "Usage: $0 <hostname/ip> <ip>" && exit 1

passwd=Huawei12#$

/usr/bin/expect<<-EOF
	spawn ssh $1 ipmcset -d ipaddr -v 172.17.40.$2  255.255.0.0
	expect {
		"(yes/no)?" { send "yes\r"; exp_continue }
		"password:" { send "${passwd}\r" }
	}
	expect eof
	EOF

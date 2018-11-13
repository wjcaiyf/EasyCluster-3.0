#!/bin/bash

rm -rf /root/.ssh

[ $# -ne 1 ] && echo "Usage: $0 hostname/ip" && exit 1

passwd=Huawei12#$

/usr/bin/expect<<-EOF
	spawn ssh $1 ipmcset -d activeport -v 1 1
	expect {
		"(yes/no)?" { send "yes\r"; exp_continue }
		"password:" { send "${passwd}\r" }
	}
	expect eof
	EOF

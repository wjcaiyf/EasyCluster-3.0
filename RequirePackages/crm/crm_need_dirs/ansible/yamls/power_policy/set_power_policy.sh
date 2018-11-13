#!/bin/bash

Usage () {
    cat <<-EOF
	Usage: $0 -c common_prefix -b begin -e end [ -s common_suffix ] [ -u ipmi_user ] [ -p ipmi_password ]

	Options:
	-c	common prefix
	-b	begin  number
	-e	end number
	-s	default: empty("")
	-u 	default: "root"
	-p 	default: "Huawei12#$"
    
	example:

	1: $0 -c nd -b 1 -e 100                  // nd001 to nd100  without common_suffix
	2: $0 -c ne0 -b 1 -e 56 -s -bmc          // ne001-bmc to ne056-bmc  with common_suffix
	3: $0 -c nd -b 2 -e 46                   // nd02 to nd46 without common_suffix
	4: $0 -c node -b 1 -e 20 -p admin        // node01 to node20 without common_suffix and ipmi_password is "admin"

	EOF
    exit 1
}

color () {
    if [ "$1" = "red" ];then
	echo -e "\033[31m[Error]: $2."
	echo -e "\033[0m"
        Usage
    fi
    if [ "$1" = "green" ];then
	echo -e "\033[32m$2."
	echo -e "\033[0m"
    fi
}

if [ $# -eq 0 ]; then
    Usage
fi

cs=''
user=root
password=Huawei12#$

while getopts "c:b:e:s:u:p:h" flag; do  
    case "${flag}" in  
        c)  
            cp=$OPTARG  
        ;;  
        b)  
            begin=$OPTARG  
        ;;  
        e)  
            end=$OPTARG  
        ;; 
        s)  
            cs=$OPTARG
        ;;  
        u)  
            user=$OPTARG  
        ;;  
        p)  
            password=$OPTARG
        ;;  
        h|?)  
             Usage  
             ;;  
    esac  
done  

[ -z "${cp:-}" ] && color red 'you must specify "-c" option'
[ -z "${begin:-}" ] && color red 'you must specify "-b" option'
[ -z "${end:-}" ] && color red 'you must specify "-e" option'

echo "$cp" | grep -q "[0-9]" && color red '< common_prefix > must be a pure "character"'
[ -n "`echo $begin | tr -d '[0-9]'`" ] && color red '< begin > must be a pure "number"'
[ -n "`echo $end | tr -d '[0-9]'`" ] && color red '< end > must be a pure "number"'
[ $begin -gt $end ] && color red '<begin> must be Less than equal to or equal to <end>'

num_length=`expr length $end`

for i in `seq $begin $end`
do
  host=`printf "${cp}%0${num_length}d${cs}\n" $i`
  (ipmitool -I lanplus -H ${host} -U ${user} -P ${password} chassis policy previous) &
done

wait

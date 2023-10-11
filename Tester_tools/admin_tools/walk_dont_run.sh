#!/bin/bash

HW_INFO="cat /sys/devices/virtual/dmi/id/product_name"
CPU_INFO="lscpu|egrep 'Arch|Core|Socket'|paste -d';' - - - -|tr -s ' '"
MEM_INFO="free -h|grep Mem|awk '{print \$1,\$2}'"
NET_INFO="lspci|grep Ethernet"
OS_INFO="cat /proc/version"; #lsb_release -a #cat /etc/os-release #cat /etc/issue
GCC_INFO="gcc --version|grep -i gcc"
JAVA_INFO=""


while IFS="," read -r HOST
do
  echo $HOST
  ssh $HOST "$HW_INFO;$CPU_INFO;$MEM_INFO;$NET_INFO;$OS_INFO;$GCC_INFO" < /dev/null
  echo "==========="
done < input.csv
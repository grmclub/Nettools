#!/bin/bash

HW_INFO="cat /sys/devices/virtual/dmi/id/product_name"
CPU_INFO="lscpu|egrep 'Arch|Core|Socket|Model'|paste -d';' - - - -|tr -s ' '"
MEM_INFO="free -h|grep Mem|awk '{print \$1,\$2}'"
NET_INFO="lspci|grep Ethernet"
DISK_INFO="lsblk -d -o NAME,SERIAL,SIZE"
OS_INFO="lsb_release -a|grep Desc"; #cat /proc/version #cat /etc/os-release #cat /etc/issue
GCC_INFO="gcc --version|grep -i gcc"
JAVA_INFO="env|grep -i java_home"
INPUT_FILE=""

sweep_hosts()
{
    input_file="$1"
    while IFS="," read -r HOST
    do
      echo "Host:$HOST"
      ssh $HOST "$HW_INFO;$CPU_INFO;$MEM_INFO;$OS_INFO;$NET_INFO;$GCC_INFO" < /dev/null
      echo "==========="
    done < $input_file
}

usage()
{
     cat <<-EOF
     usage: $0 -f <arg>

     OPTIONS:
         -f   Host list file
         -h   Display this help message.
EOF
exit 0

}

function main()
{
    while getopts hf:? opt
    do
        case ${opt} in
            f) INPUT_FILE=${OPTARG}; ;;
            h|?) usage;           ;;
        esac
    done

    ### Parameter check
    if [[ -n ${INPUT_FILE} ]]; then sweep_hosts "$INPUT_FILE"; fi

    exit 0
}

main "$@"

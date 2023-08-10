#!/bin/bash
#set -eux
set -eu

# vim:ts=4:sw=4:et

: ${RANGE=""}
: ${IP=""}
: ${NIC=""}
: ${OUTFILE="xx"}

TODAY=$(date "+%Y%m%d");

function filter1(){
    tcpslice /var/xx/dump-$NIC-$(date -I)-*.tcpdump | tcpdump -r - "portrange $RANGE or (vlan and portrange $RANGE)" -w $OUTFILE.pcap

}

function filter2(){
    tcpslice /var/xx/dump-$NIC-$(date -I)-*.tcpdump | tcpdump -r - "host $IP  or (vlan and host $IP)  " -w $OUTFILE.pcap

}

usage()
{
     cat <<-EOF
     usage: $0 -n <arg> -o <arg> -r <arg> -i <arg>

     OPTIONS:
         -i   IP address
         -n   NIC Interface (eth0, eth1)
         -o   Output filename
         -r   Port Range
         -h   Display this help message.
EOF
exit 0

}

function main()
{

    while getopts hi:n:o:r:? opt
    do
        case ${opt} in
            i) IP=${OPTARG};      ;;
            n) NIC=${OPTARG};     ;;
            o) OUTFILE=${OPTARG}; ;;
            r) RANGE=${OPTARG};   ;;
            h|?) usage;           ;;
        esac
    done

    ### Parameter check
    if [[ -z ${NIC} ]]; then usage; fi
    if [[ -z ${RANGE} && -z ${IP}  ]]; then usage; fi

    if [[ -n ${RANGE} ]]; then filter1; fi
    if [[ -n ${IP} ]]; then filter2; fi
    exit 0
}

main "$@"

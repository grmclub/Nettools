#!/bin/bash

# ./px.sh -f 20000 -l 20002
# ./px.sh -s
#


FPORT=""
LPORT=""
IP="0.0.0.0"
STOP_FLAG=false

function usage(){
     cat <<-EOF
     usage: $0 -f <arg> -l <arg> -h <arg> -s

     OPTIONS:
         -f   First listening port
         -l   Last listening port
         -s   Stop listening ports
         -h   Display this help message.
EOF
exit 0

}

function start_listening(){
    echo "Bringing up ports"
	for (( i = FPORT; i <= LPORT; i++ )); do
		#echo "nc -l -k $i &
        echo "Listen port: $i up"
		nc -l -k $i &
	done
}


function stop_listening(){
    echo "Stopping listening ports"
    killall -e nc
    exit 0;
}

function main()
{
    ### Set parameters
    while getopts hi:f:l:r:s? opt
    do
        case ${opt} in
            i) IP=${OPTARG};      ;;
            f) FPORT=${OPTARG};   ;;
            l) LPORT=${OPTARG};   ;;
            s) STOP_FLAG=true     ;;
            h|?) usage;           ;;
        esac
    done

    ### Parameter check
    if ${STOP_FLAG} ;then
        stop_listening
    elif [[ -z ${FPORT}  ]] || [[ -z ${LPORT} ]];then
        echo "Stage--1"
        usage;
    elif [[ ${FPORT} -le 0  ]] || [[ ${LPORT} -le 0 ]];then
        echo "Stage--2"
        usage;
    else
        start_listening
    fi

    exit 0
}

main "$@"


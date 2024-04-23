#!/bin/bash
# taskset -c 5 ./rej.sh -f rej.pcap

set -eu

filter_ouch_rejects(){

    file="$1"
    fn="${file%%.*}_rej.txt"

    tshark -r $file  \
    -Y "ouch.message_type == J" \
    -Tfields  -E header=y  -E separator='|' \
    -e tcp.port \
    -e ouch.message_type \
    -e ouch.timestamp \
    -e ouch.order_token \
    -e ouch.reason > $fn

    awk -F'|' '{print $5}' $fn| sort | uniq -c

}

usage()
{
     cat <<-EOF
     usage: $0 -f <arg>

     OPTIONS:
         -f   Filename to dissect
         -h   Display this help message.
EOF
exit 0

}


main()
{
    : ${FILE=""}

    ## Set Parameters
    while getopts hf:? opt
    do
        case ${opt} in
            f) FILE=${OPTARG};    ;;
            h|?) usage;           ;;
        esac
    done

    #echo " Testdir: ${FUNC} dt: ${BOARD}  wait: ${REFNUM}"

    ### Parameter check
    if [[ -z ${FILE} ]]; then usage;

    else
        filter_ouch_rejects ${FILE}
    fi

    exit 0
}

main "$@"

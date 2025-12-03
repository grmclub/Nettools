#!/bin/bash
#set -eux
set -eu

# vim:ts=4:sw=4:et
# :%s=\s\+$==

: ${RANGE=""}
: ${IP=""}
: ${NIC=""}
: ${OUTFILE="xx"}

TODAY=$(date "+%Y%m%d");

##Send mail
send_mail()
{
	send_from="xx@yahoo.com"
	send_to="xx@gmail.com"
	cc_to=""
	bcc_to=""
	tm=$(date +%H%M)

	sub="XX Report for $TODAY"
	body="Please find file(s) attached"
	echo $body| mailx -r $send_from -c $cc_to -b $bcc_to -a "$file1" -a "$file2" $send_to
	echo "Mail sent"
}

##Auto cleanup old files
cleanup_dir()
{
	day_of_week=$(date +%w)
	days_before=7
	if [[ day_of_week == "1" ]]; then
		days_before=10
	fi
	cmd="find $data_dir -mtime +${days_before} -delete"
	echo $cmd|ssh ${sync_host}
}

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

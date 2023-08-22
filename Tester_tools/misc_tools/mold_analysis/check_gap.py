#!/usr/bin/env python

# --Filter Pri/Sec Mold Feed
#ip="239.72.1.2" / ip="239.72.2.2"
#
# --To pre Filter
# taskset -c 5 tcpslice *.tcpdump | tcpdump -r - "host 239.72.1.2  or (vlan and host 239.72.1.2) " -w itch-pri.pcap
#
# --Extract Seqno
#taskset -c 5 \
#tcpslice *.tcpdump | tshark -nr - \
#    -Y "ip.addr == 239.72.1.2" \
#    -E header=y  -E separator='|'
#    -Tfields \
#    -e frame.time_epoch \
#    -e moldudp64.sequence \
#    -e moldudp64.count \
#    -e itch.message_type
#


import os
import sys
import getopt
import errno

import csv
import time
import subprocess

def execCmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.returncode
    return (ret, output, err)

def process_pcap_file(pcap_file, data_file, filter_ip):
    cmd="""taskset -c 3 \
        tshark -r %s \
        -Y "ip.addr == %s" \
        -E separator='|' \
        -Tfields \
        -e frame.time_epoch \
        -e moldudp64.sequence \
        -e moldudp64.count \
        -e itch.message_type > %s """ %(pcap_file, filter_ip, data_file)

    print "Processing pcap file: %s" % pcap_file
    (ret,out,err) = execCmd(cmd)
    return

def process_file(data_file):
    with open(data_file, "rb") as ifile:
        reader = csv.reader(ifile, delimiter='|', quotechar='"')
        print "Processing data file: %s" % data_file

        seqno_cnt = 0
        gapflag = False
        row_cnt =0
        for row in reader:
            row_cnt    = row_cnt +1
            itch_time  = row[0]
            itch_seqno = int(row[1])
            msg_count  = int(row[2])
            msg_type   = row[3]
            #print "%s,%s,%s,%s" % (row[0], row[1], row[2],row[3])

            if seqno_cnt == 0:
                seqno_cnt = itch_seqno
                print "Set initial seq no."

            if seqno_cnt != itch_seqno:
                i,d = itch_time.split('.')
                itch_time = time.strftime('%H:%M:%S', time.localtime(float(itch_time)))
                print "Row: %d Time: %s.%s Exp Seqno: %s Rcvd Seqno: %s" % ( row_cnt, itch_time, d, seqno_cnt, itch_seqno)
                seqno_cnt = itch_seqno
                gapflag = True

            seqno_cnt = seqno_cnt + msg_count

        if not gapflag:
            print "No Seq.gap found in data file: %s" % data_file


def printHelp():
    app_name = os.path.basename(__file__) # sys.argv[0]
    print """Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -i  IP address to filter
         -p  pcap input file
         -h  Display this help message.
    Ex:
    %s -p xx.pcap -i 239.72.1.2 -f xx.dat

    """ % (app_name, app_name)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:p:i:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        DATA_FILE = "seq.dat"
        PCAP_FILE = ""
        FILTER_IP = ""
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-p":
                PCAP_FILE = a
            if o == "-i":
                FILTER_IP = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        if PCAP_FILE:
            process_pcap_file(PCAP_FILE, DATA_FILE, FILTER_IP)

        process_file(DATA_FILE)


    except Exception, err:
        print("Error::main: %s\n" %str(err))
        sys.exit(3)

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import os
import sys
import getopt
import errno

import math
import subprocess
from collections import defaultdict
import csv
from decimal import Decimal

# --latency calc format
#
#frame.time_epoch|tcp.dstport|ouch.message_type|ouch.order_token|ouch.order_reference_number
#1464651328.487931000|21483|O|920000003|
#1464651328.487967000|15509|A|920000003|201605310000001137


class orderLatency:
    def __init__(self,order_refno, token, dstport, sendtime, acktime, msgtype, delay):
        self.m_order_refno = order_refno
        self.m_token       = token
        self.m_dstport     = dstport
        self.m_sendtime    = Decimal(sendtime)
        self.m_acktime     = Decimal(acktime)
        self.m_msgtype     = msgtype
        self.m_delay       = delay

    def updateData(self, order_refno, acktime, msgtype):
        self.m_order_refno = order_refno
        self.m_acktime     = Decimal(acktime)
        self.m_msgtype     = self.m_msgtype + msgtype
        self.m_delay       = self.m_acktime - self.m_sendtime


    def output(self):
       return "%s, %s, %s, %f, %f, %s, %f\n" % (self.m_order_refno,
                                                self.m_token,
                                                self.m_dstport,
                                                self.m_sendtime,
                                                self.m_acktime,
                                                self.m_msgtype,
                                                self.m_delay)

    def __str__(self):
        return ", ".join([str(self.m_order_refno),
                          self.m_token,
                          self.m_dstport,
                          str(self.m_sendtime),
                          str(self.m_acktime),
                          self.m_msgtype,
                          str(self.m_delay)])

def execCmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.returncode
    return (ret, output, err)

def process_pcap_file(pcap_file, data_file):
    cmd="""tshark -r %s \
          -Y "(soupbintcp.packet_type == 83 || soupbintcp.packet_type == 85) && ouch.message_type != S" \
          -Tfields -E header=y -E separator='|' \
          -e frame.time_epoch        \
          -e tcp.dstport             \
          -e ouch.message_type   \
          -e ouch.order_token    \
          -e ouch.order_reference_number > %s """ %(pcap_file, data_file)

    (ret,out,err) = execCmd(cmd)
    return

def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * Decimal((c-k))
    d1 = key(N[int(c)]) * Decimal((k-f))
    return d0+d1


def process_file(data_file):
    ifile  = open(data_file, "rb")
    reader = csv.reader(ifile, delimiter='|' )

    rowflag     = 0
    time        = 0
    dstport     = 0
    msgtype     = ""
    token       = 0
    order_refno = ""

    oe_dict = {}

    for time,      \
        dstport,   \
        msgtype,   \
        token,     \
        order_refno  in reader:

        if rowflag == 1:
             if token in oe_dict:
                if    msgtype == 'A'  \
                   or msgtype == 'E'  \
                   or msgtype == 'U'  \
                   or msgtype == 'X'  \
                   or msgtype == 'J':

                    order = oe_dict[token]
                    if order.m_order_refno == 0:
                        order.updateData(order_refno, time, msgtype)
             else:
                #(order_refno, token, dstport, sendtime, acktime, msgtype, delay):
                if msgtype == 'O' or msgtype == 'U' or msgtype == 'C':
                    oe_dict[token] = orderLatency(0, token, dstport, time,  0, msgtype, 0)
        else:
            rowflag = 1 # skip header

    ifile.close()

    ##Filter and remove untracable orders
    rm_key = []
    for key in oe_dict.iterkeys():
        order = oe_dict[key]
        if order.m_order_refno == "" or order.m_order_refno == 0 or order.m_delay == 0:
            rm_key.append(key)

    for key in rm_key:
        del oe_dict[key]

    ##Calculate latency stats
    items = sorted(oe_dict.values(), key=lambda x: x.m_delay, reverse=True)
    size = len(items)
    min_l = Decimal(items[size-1].m_delay)
    max_l = Decimal(items[0].m_delay)
    sum_l = sum(item.m_delay for item in items)
    avg_l = Decimal(sum_l/size)
    time_diff_list = [item.m_delay for item in items]

    percentile50  = percentile(time_diff_list,0.5)
    percentile90  = percentile(time_diff_list,0.9)
    percentile95  = percentile(time_diff_list,0.95)
    percentile99  = percentile(time_diff_list,0.99)
    percentile999 = percentile(time_diff_list,0.999)

   # print "sum=%f avg=%.6f, min=%.6f, max=%.6f" %(sum_l, avg_l, min_l, max_l)
    print "avg=%.6f, min=%.6f, max=%.6f 50%%=%.6f 90%%=%.6f 95%%=%.6f 99%%=%.6f 99.9%%=%.6f" % \
          ( avg_l ,min_l ,max_l, \
            percentile50, percentile90, percentile95, percentile99, percentile999)


    #print row
    #for key in oe_dict.iterkeys():
    #    print oe_dict[key]
    #for item in items:
    #    print item

    latency_file = os.path.splitext(data_file)[0] + '.dat'
    with open(latency_file, 'w') as f:
        for item in items:
            f.write(item.output())

    print "Done writing..."


def printHelp():
    print """Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -p  pcap input file
         -h  Display this help message.
    """ % os.path.basename(__file__)  # sys.argv[0]


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:f:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        DATA_FILE = "latency.csv"
        PCAP_FILE = ""
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-p":
                PCAP_FILE = a
            if o == "-h":
                printHelp()
                sys.exit(0)


        if PCAP_FILE:
            process_pcap_file(PCAP_FILE, DATA_FILE)

        process_file(DATA_FILE)

    except Exception, err:
        print("Error::main: %s\n" %str(err))
        sys.exit(3)

if __name__ == "__main__":
    main()

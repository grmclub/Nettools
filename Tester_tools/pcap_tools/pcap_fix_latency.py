#!/usr/bin/env python

import os, sys, getopt
import errno,traceback
import subprocess
import re
from collections import OrderedDict
from datetime import *
import csv

def printHelp():
    print """Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -h  Display this help message

    #Extract data with
    tshark -r $file -R "tcp.port == $port" \
    -T fields \
    -Eseparator=, \
    -Eoccurrence=l \
    -e frame.time_epoch \
    -e ip.src\
    -e tcp.srcport \
    -e ip.dst \
    -e tcp.dstport \
    -e fix.MsgType \
    -e fix.ClOrdID \
    -e fix.OrderID \
    -e fix.OrdStatus \
    -e fix.SenderCompID \
    -e fix.SenderSubID \
    -e fix.TargetCompID \
    -e fix.Symbol \
    -e fix.Side \
    -e fix.Price \
    -e fix.OrderQty   > ${port}_ext

    """ % os.path.basename(__file__)  # sys.argv[0]
    sys.exit(1)

def percentile_calc(N,percent):
    if not N:
        return None
    k = len(N) * percent
    return N[int(k-1)]

def calc_latency(session,sess_list):
    sess_list.sort()
    p50 = percentile_calc(sess_list,0.50)
    p80 = percentile_calc(sess_list,0.80)
    p90 = percentile_calc(sess_list,0.90)
    p95 = percentile_calc(sess_list,0.95)
    p99 = percentile_calc(sess_list,0.99)
    pmax = len(sess_list) -1
    print("Session,Data_Size,50,80,90,95,99,Max")
    print("%s,%d,%s,%s,%s,%s,%s,%s" %(session,len(sess_list),p50,p80,p90,p95,p99,sess_list[pmax]))


def process_file(data_file):
    id_dict = {}
    with open(data_file, "r") as ifile:
        reader = csv.reader(ifile)
        for row in reader:
            msgtype = row[5]
            session = row[9]
            ClOrdId = row[6]
            ord_status = row[8]
            dt_time = row[0]
            tnx_time = float(row[0])

            #print session,msgtype,ClOrdId,ord_status,tnx_time
            if msgtype =="D":
                session = row[9]
                id_dict[ClOrdId] = {"t1":tnx_time, "t2":"", "time_diff":"", "token": session + '.' + ClOrdId, "dt_time":dt_time}
            if msgtype == '8' and ord_status == '0':
                if id_dict.get(ClOrdId):
                id_dict[ClOrdId]["t2"] = tnx_time
                t1 = (id_dict[ClOrdId]["t1"])
                t2 = (id_dict[ClOrdId]["t2"])
                delay = abs(t2 -t1)
                id_dict[ClOrdId]["time_diff"] = "%0.9f" % delay

    sorted_dict = OrderedDict(sorted(id_dict.items(), key=lambda t:t[1]["time_diff]))
    sorted_list = []
    sess = ""
    for key,val in sorted_dict.items():
        print val
        if val["time_diff"] != "":
            sorted_list.append(val["time_diff"])
        sess = ses.split('.')
        if sess[0] != '':
            calc_latency(sess[0],sorted_list)



def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        DATA_FILE = ""
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        process_file(DATA_FILE)

    except Exception, err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()

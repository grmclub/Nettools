#!/usr/bin/env python


import os
import sys
import getopt
import errno

import csv
from decimal import Decimal

def gen_msg_rate_us(data_file):
    group_us = 0
    count_us = 0

    row_flag = True
    ifile  = open(data_file, "rb")
    reader = csv.reader(ifile)

    for row in reader:
        #print '%d,%d,%s' % (int(Decimal(row[0])), int(Decimal(row[0]) * 1000), row[1])
        #latency_ms  = int(Decimal(row[6]) * 1000)
        latency_us  = int(Decimal(row[6]) * 1000000)
        #print row[6] +" :  " + str(latency_us)
        #sys.exit()
        if row_flag :
            row_flag  = False
            group_us  = latency_us
            count_us  = 1

        else :
            if group_us == latency_us:
                count_us = count_us + 1

            else :
                print "%d,%d" % (group_us, count_us)

                count_us = 1
                group_us = latency_us


    print "%d,%d" % (group_us, count_us)
    ifile.close()

def gen_msg_rate_ms(data_file):
    sum_sec   = 0
    sum_ms    = 0
    group_sec = 0
    group_ms  = 0
    max_ms    = 0

    row_flag = True
    ifile  = open(data_file, "rb")
    reader = csv.reader(ifile)

    for row in reader:
        #print '%d,%d,%s' % (int(Decimal(row[0])), int(Decimal(row[0]) * 1000), row[1])
        time_sec = int(Decimal(row[0]))
        time_ms  = int(Decimal(row[0]) * 1000)

        if row_flag :
            row_flag = False
            group_sec = time_sec
            group_ms  = time_ms
            sum_sec = sum_sec + 1
            sum_ms  = sum_ms  + 1
            max_ms  = sum_ms

        else :
            if group_sec == time_sec:
                sum_sec = sum_sec + 1

                if group_ms == time_ms:
                    sum_ms = sum_ms + 1
                else :
                    if max_ms < sum_ms:
                        max_ms = sum_ms

                    sum_ms = 1
                    group_ms = time_ms

            else :
                ## multiply max_ms by 1000 to project over 1 sec
                print "%d,%d,%d" % (group_sec, sum_sec, max_ms*1000)

                sum_sec = 1
                max_ms  = 0
                group_sec = time_sec


    print "%d,%d,%d" % (group_sec, sum_sec, sum_ms)
    ifile.close()


def gen_msg_rate_sec(data_file):
    sum_sec   = 0
    group_sec = 0

    row_flag = True
    ifile  = open(data_file, "rb")
    reader = csv.reader(ifile)

    for row in reader:
        time_sec = int(Decimal(row[0]))

        if row_flag :
            row_flag = False
            group_sec = time_sec
            sum_sec = sum_sec + 1

        else :
            if group_sec == time_sec:
                sum_sec = sum_sec + 1

            else :
                print "%d,%d" % (group_sec, sum_sec)

                sum_sec = 1
                group_sec = time_sec

    print "%d,%d,%d" % (group_sec, sum_sec, sum_ms)
    ifile.close()


def process_file(data_file, select_interval):
    if (select_interval == 'ms'):
        gen_msg_rate_ms(data_file)

    elif (select_interval == 'us'):
        gen_msg_rate_us(data_file)

    elif (select_interval == 's'):
        gen_msg_rate_sec(data_file)

    else:
        print "Invalid Plot interval selected"
        sys.exit(1)


def printHelp():
    print """Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -p  plot interval (sec: s, millisec: ms, microsec: us)
         -h  display this help message.
    """ % os.path.basename(__file__)  # sys.argv[0]

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:f:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        DATA_FILE = ""
        INTERVAL_SELECT = ""
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-p":
                INTERVAL_SELECT = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        process_file(DATA_FILE, INTERVAL_SELECT)

    except Exception, err:
        print("Error::main: %s\n" %str(err))
        sys.exit(3)

if __name__ == "__main__":
    main()


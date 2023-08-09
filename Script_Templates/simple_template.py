#!/usr/bin/env python

#import os, sys, getopt
import os
import sys
import getopt
import errno
import traceback

def printHelp():
    print """Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -h  Display this help message.
    """ % os.path.basename(__file__)  # sys.argv[0]

import csv
from decimal import Decimal


def process_file(data_file):
    ifile  = open(data_file, "rb")
    reader = csv.reader(ifile)

    rownum = 0
    for row in reader:
        # Save header row.
        if rownum == 0:
            header = row
        else:
            colnum = 0
            bp = row[7].replace(',', '')
            ul = row[8].replace(',', '')
            ll = row[9].replace(',', '')
            print '%s,%g,%g,%g' % (row[0], Decimal(bp) *10, Decimal(ul) *10, Decimal(ll) *10)
        rownum = 1
    ifile.close()

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

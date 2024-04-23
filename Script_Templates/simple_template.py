#!/usr/bin/env python

import os, sys, getopt
import errno, traceback
import csv
from decimal import Decimal
import subprocess


def printHelp():
    print ("""Usage: %s -f <filename>

    OPTIONS:
         -f  host list file
         -h  Display this help message.
    """ % os.path.basename(__file__))

def execCmd(cmd):
    #print (cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.returncode
    return (output,err,ret)

class Item:
    self.m_code
    self.m_price
    self.m_desc

    def __init__(self):
        self.m_price = 0
        self.m_name  = ""

    def __init__(self, price, name):
        self.m_price = price
        self.m_name  = name

def printHelp():
    print ("""Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -h  Display this help message.
    """ % os.path.basename(__file__))


def process_file(data_file):
    with open(data_file, "r") as ifile:
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
                print('%s,%g,%g,%g' % (row[0], Decimal(bp) *10, Decimal(ul) *10, Decimal(ll) *10))
            rownum = 1

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h")
    except getopt.GetoptError as e:
        print (e)
        sys.exit()

    try:
        DATA_FILE = ""
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        if (DATA_FILE):
            process_file(DATA_FILE)

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()

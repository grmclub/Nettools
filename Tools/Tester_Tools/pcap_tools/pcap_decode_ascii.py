#!/usr/bin/env python

import os, sys, getopt
import errno,traceback
import subprocess
import re
from datetime import *
import struct
import binascii

def printHelp():
    print (("""Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -p  pcap file
         -h  Display this help message.
    """) % (os.path.basename(__file__)))  # sys.argv[0]

def execCmd(cmd):
    print (cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.returncode
    return (ret, output, err)

def extract_from_pcap_file(pcap_file,out_file):
    cmd = """tshark -r %s \
    -T fields \
    -Eseparator='|' \
    -Eoccurrence=l \
    -e frame.time \
    -e data > %s """ % (pcap_file,out_file)
    result,e,r = execCmd(cmd)

def process_file(data_file):
    with open(data_file, "r") as ifile:
        for line in ifile:
            row = line.split('|')
            row_len = len(row)
            ts = "x"
            if row_len == 2:
                ts = row[0]
                line = row[1].strip()
            else:
                line = row[0].strip()

            if len(line) > 1:
                buf = bytearray.fromhex(line.strip())
                print("%s,%s" % (ts,buf))
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:p:h")
    except getopt.GetoptError as e:
        print (e)
        sys.exit()

    try:
        DATA_FILE = ""
        PCAP_FILE = ""
        OUT_FILE  = "./ext.bin"
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-p":
                PCAP_FILE = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        if PCAP_FILE != "":
            extract_from_pcap_file(PCAP_FILE,OUT_FILE)
            DATA_FILE = OUT_FILE
        process_file(DATA_FILE)

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()

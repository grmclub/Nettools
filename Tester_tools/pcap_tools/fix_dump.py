#!/usr/bin/env python3

# Modified from: http://stackoverflow.com/questions/13810156/tshark-export-fix-messages
# download scapy from http://www.secdev.org/projects/scapy/
# alternative extracton method:
# tshark -nr fix.pcap -Y'fix' -w- | tcpdump -r- -l -w- | tcpflow -r- -C -B  | tr \\001  '|'
#

import os
import sys
import getopt
import re
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

def ExtractFIX(pcap):
    """A generator that iterates over the packets in a scapy pcap iterable
and extracts the FIX messages.
In the case where there are multiple FIX messages in one packet, yield each
FIX message individually."""
    for packet in pcap:
        if packet.haslayer('Raw'):
            # Only consider TCP packets which contain raw data.
            payload = packet.getlayer('Raw').load
            payload = str(payload, encoding='utf-8')
            # Ignore raw data that doesn't contain FIX.
            if not 'FIX' in payload:
                continue

            # Replace \x01 with '|'.
            payload = re.sub(r'\x01', '|', payload)

            # Split out each individual FIX message in the packet by putting a
            # ';' between them and then using split(';').
            for subMessage in re.sub(r'\|8=FIX', '|;8=FIX', payload).split(';'):
                # Yield each sub message. More often than not, there will only be one.
                assert subMessage[-1:] == '|'
                yield subMessage
        else:
            continue


def printHelp():
    print ("""Usage: %s -f <arg> <arg> -h

    OPTIONS:
         -f  pcap file
         -h  Display this help message.
    """ % os.path.basename(__file__))  # sys.argv[0]


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h")
    except getopt.GetoptError as e:
        print(e)
        sys.exit()

    capture_file=""
    for o,a in opts:
        if o == "-f":
            capture_file = a
        if o == "-h":
            printHelp()
            sys.exit(0)

    try:
        #parse file
        if os.path.isfile(capture_file) and os.access(capture_file, os.R_OK):
            #pcap = rdpcap(capture_file)
            pcap = PcapReader(capture_file)
            for fixMessage in ExtractFIX(pcap):
                print(fixMessage)
            print("")
        else:
            raise "Either file is missing or is not readable"

    except Exception as err:
        print("Error::main: %s\n" %str(err))
        sys.exit(3)

if __name__ == "__main__":
    main()


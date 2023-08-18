#!/usr/bin/env python

import os, sys, getopt
import errno,traceback
import subprocess
import re
from datetime import *
import struct
import binascii


def printHelp():
    print """Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -p  pcap file
         -h  Display this help message.
    """ % os.path.basename(__file__)  # sys.argv[0]


def execCmd(cmd):
    print (cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.returncode
    return (ret, output, err)

data_list = []

#class chixj_ouch
#class asx_ouch

# --add ts
# --add logic for decoding multiple soup packets in a tcp pkt
# --add decoders for other markets


class jnx_ouch:
    def __init__(self,buf):
        self.header = struct.unpack('>Hcc', buf[0:4])
        self.size = int(self.header[0])
        self.soup_pkt_type = self.header[1]
        self.ouch_msg_type = self.header[2]
        self.ouch_buf = buf[4:]
        self.buf_len = len(buf)
        #print("Buf_len=%d" % (self.buf_len))
        #print(data_len=%d,size=%d" % (len(buf),self.size))

    def print_headers(self):
        print(self.size,self.soup_pkt_type,self.ouch_msg_type)

    def decode(self):
        ext = ""
        if self.buf_len >=4:
            ouch_buf = self.ouch_buf[0:self.size]
            #self.print_headers()
            if self.ouch_msg_type == 'O':
                ext = self.output_msg(ouch_buf, '>I10scII4sIIIccIcc')
            elif self.ouch_msg_type == 'U' and self.soup_pkt_type == 'U':
                ext = self.output_msg(ouch_buf, '>IIIIIcI')
            elif self.ouch_msg_type == 'X':
                ext = self.output_msg(ouch_buf, '>II')
            elif self.ouch_msg_type == 'A':
                ext = self.output_msg(ouch_buf[0:64], '>QI10scII4sIIIccQIccc')
            elif self.ouch_msg_type == 'C':
                ext = self.output_msg(ouch_buf, '>QIIc')
            elif self.ouch_msg_type == 'U'  and self.soup_pkt_type == 'S':
                ext = self.output_msg(ouch_buf[0:51], '>QIcII4sIIcQIcI')
            elif self.ouch_msg_type == 'D':
                ext = self.output_msg(ouch_buf, '>QIIcIIc')
            elif self.ouch_msg_type == 'E':
                ext = self.output_msg(ouch_buf[0:29], '>QIIIcQ')
            elif self.ouch_msg_type == 'J':
                ext = self.output_msg(ouch_buf, '>QIc')
            elif self.ouch_msg_type == 'S':
                ext = self.output_msg(ouch_buf, '>Qc')
        return ext

    def output_msg(self,buf,unpack_str):
        global data_list
        del data_list
        data_list = struct.unpack(unpack_str, buf)
        return("%d,%s,%s,%s"% (self.header[0],self.header[1],self.header[2], ",".join(str(x) for x in data_list)))


class soupbintcp:
    def __init__(self,app_handler):
        self.app_handler = app_handler

    def decode(self,buf):
        buf_len = len(buf)
        ext = ""
        if buf_len >=3:
            size,soup_pkt_type = struct.unpack('>Hc', buf[0:3])
            soup_buf = buf[4:]
            soup_buf = soup_buf[0:size]
            #if (buf_len != size +2):
            #   print("Buf_len=%d" %(buf_len))
            #self.output_hdr(size,soup_pkt_type)
            if soup_pkt_type == '+':
                ext = self.output_hdr(size,soup_pkt_type)
            elif soup_pkt_type == 'H':
                ext = self.output_hdr(size,soup_pkt_type)
            elif soup_pkt_type == 'R':
                ext = self.output_hdr(size,soup_pkt_type)
            elif soup_pkt_type == 'Z':
                ext = self.output_hdr(size,soup_pkt_type)
            elif soup_pkt_type == 'L':
                ext = self.output_hdr(size,soup_pkt_type)
                #self.output_soup(size,soup_pkt_type,soup_buf[0:45],'6s10s10s20s')  ##XXX -Fix
            elif soup_pkt_type == 'A':
                ext = self.output_hdr(size,soup_pkt_type)
                #self.output_soup(size,soup_pkt_type,soup_buf,'10s20s')  ##XXX -Fix
            elif soup_pkt_type == 'J':
                ext = self.output_soup(size,soup_pkt_type,soup_buf,'c')
            elif soup_pkt_type == 'O':
                ext = self.output_hdr(size,soup_pkt_type)
            elif soup_pkt_type == 'S':
                handler = jnx_ouch(buf)
                ext = handler.decode()
            elif soup_pkt_type == 'U':
                handler = jnx_ouch(buf)
                ext = handler.decode()
        return ext


    def output_hdr(self,size,pkt_type):
        return ("%d,%s" % (size,pkt_type))

    def output_soup(self,size,pkt_type,buf,unpack_str):
        data_list = struct.unpack(unpack_str,buf)
        return("%d,%s,%s"% (size,pkt_type, ",".join(str(x) for x in data_list)))


def extract_from_pcap_file(pcap_file,out_file):
    cmd = """tshark -r %s \
    -T fields \
    -Eseparator=, \
    -Eoccurrence=l \
    -e frame.time_epoch \
    -e data > %s """ % (pcap_file,out_file)
    result,e,r = execCmd(cmd)



def process_file(data_file):
    app_handler = "jnx_ouch"
    soup_handler = soupbintcp(app_handler)
    with open(data_file, "r") as ifile:
        for line in ifile:
            row = line.split(',')
            row_len = len(row)
            ts = "x"
            if row_len == 2:
                ts = row[0]
                line = row[1].strip()
            else:
                line = row[0].strip()

            if len(line) > 1:
                buf = bytearray.fromhex(line.strip())
                ext = soup_handler.decode(buf)
                print("%s,%s" % (ts,ext))


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:p:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        DATA_FILE = ""
        PCAP_FILE = ""
        OUT_FILE  = "./ext.bin"
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-f":
                PCAP_FILE = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        if PCAP_FILE != "":
            extract_from_pcap_file(PCAP_FILE,OUT_FILE)
            DATA_FILE = OUT_FILE
        process_file(DATA_FILE)

    except Exception, err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
'''
    Test Login & send heartbeats
'''
import getopt
import sys
import socket
import time
import threading

__AppName__ = "fix_tester"
msgseqnum_cnt = 0
clordid_cnt = 0
SEP="\001"

def getmsgseqnum():
    global msgseqnum_cnt
    msgseqnum_cnt += 1
    return str(msgseqnum_cnt)

def getclordid():
    global clordid_cnt
    clordid_cnt += 1
    return str(time.time()) + "_" + str(clordid_cnt)

def gettime():
    return time.strftime("%Y%m%d-%H:%M:%S", time.gmtime(time.time()))

def gettime_milli():
    now = time.time()
    localtime = time.localtime(now)
    milliseconds = '%03d' % int((now - int(now)) * 1000)
    return time.strftime('%Y%m%d-%H:%M:%S.', time.gmtime(time.time())) + milliseconds

def timestamp():
    now = time.time()
    localtime = time.localtime(now)
    milliseconds = '%03d' % int((now - int(now)) * 1000)
    return time.strftime('%Y%m%d-%H:%M:%S.', localtime) + milliseconds

def bodylen(s):
    return "9=" + str(len(s)) + SEP

def cksum(s):
    sum = 0
    for c in s:
        sum += ord(c)
    return "10=" + "%03d" % (sum % 256,) + SEP

def wrapbody(s):
    t = "8=FIX.4.2\001" + bodylen(s) + s
    return t + cksum(t)

def msg_format(st):
    return st.replace(SEP,"|")

def err_format(st):
    print timestamp() + "  " + st

def hb_send(seq_no, sender, target):

    '''
    Sample hb:
        8=FIX.4.2|9=53|35=0|34=19|49=DD1234B|52=20140828-06:05:48|56=DDXJX|10=139|
    '''
    hb_msg = wrapbody( "35=0" + SEP
                     + "34=" + seq_no + SEP
                     + "49=" + sender + SEP
                     + "52=" + gettime_milli() + SEP
                    #+ "52=" + gettime() + SEP
                     + "56=" + target + SEP
                     )
    print msg_format(hb_msg)
    return hb_msg

def printUsage():
    print __AppName__ + ":"
    print """
    -S SenderCompId
    -T TargetCompId
    -H Hostname
    -P Port
    -I Heartbeat Interval
    -D Dropcopy logon
    -u drop user
    -p drop password
    -h help

ex1 FIX : ./fix_tester.py -S DD1234B -T DNDPXX -H dhost01 -P 5002 -I 5
ex2 Drop: ./fix_tester.py -S DROP1 -T DNDPXX -H ddrop02 -P 5004 -I 5 -D -u foo -p bar
"""

def main():
    o_sender = "TEST1234"
    o_target = "DNDPXX"
    o_host   = "host01"
    o_port   = 5002
    o_hb_interval = 5
    o_drop_flag = False
    o_username  = ""
    o_password  = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:DS:T:H:P:I:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    if len(sys.argv) < 4:
        printUsage()
        sys.exit()

    for o,a in opts:
        if o == "-u":
            o_username = a
        if o == "-p":
            o_password = a
        if o == "-D":
            o_drop_flag = True
        if o == "-S":
            o_sender = a
        if o == "-T":
            o_target = a
        if o == "-H":
            o_host = a
        if o == "-P":
            o_port = a
            o_port = int(o_port)
        if o == "-I":
            o_hb_interval = a
            o_hb_interval = int(o_hb_interval)
        if o == "-h":
            printUsage()
            sys.exit()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((o_host, o_port))
        #s.setblocking(0)

    except socket.error:
        err_format("Connection to FIX GW: " + o_host + " on port: " + str(o_port) + " failed...!!")
        sys.exit()

        print "Connected"

    try:
        '''
        Sample logon:
            8=FIX.4.2|9=69|35=A|34=1|49=DD1123X|52=20140828-08:32:12|56=DDXX|98=0|108=5|141=Y|10=145|
        '''
        if (o_drop_flag):
            logon = wrapbody(  "35=A" + SEP
                             + "34=" + getmsgseqnum()      + SEP
                             + "49=" + o_sender            + SEP
                             + "52=" + gettime_milli()     + SEP
                            #+ "52=" + gettime()           + SEP
                             + "56=" + o_target            + SEP
                             + "98=0"                      + SEP
                             + "108=" + str(o_hb_interval) + SEP
                             + "553=" + o_username         + SEP
                             + "554=" + o_password         + SEP
                             + "141=Y"                     + SEP
                            )
        else:
            logon = wrapbody(  "35=A"                       + SEP
                             + "34="   + getmsgseqnum()     + SEP
                             + "49="   + o_sender           + SEP
                             + "52="   + gettime_milli()    + SEP
                            #+ "52="   + gettime()          + SEP
                             + "56="   + o_target           + SEP
                             + "98=0"                       + SEP
                             + "108="  + str(o_hb_interval) + SEP
                             + "141=Y" + SEP
                            )

        print msg_format(logon)
        s.send(logon)

        get_reply = s.recv(1024)
        print msg_format( get_reply)

        while 1:
            s.send(hb_send(getmsgseqnum(), o_sender, o_target))
            get_reply = s.recv(1024)
            print msg_format(get_reply)
            time.sleep(o_hb_interval)

    except KeyboardInterrupt:
        print "Stopping " + __AppName__ + " ...!!"

    except Exception as e:
        print "Error: ", e

    s.close()

if __name__ == "__main__":
    main()

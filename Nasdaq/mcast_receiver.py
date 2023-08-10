#!/usr/bin/env python

import base64
import getopt
import signal
import socket
import struct
import sys

# Add potentially missing socket option definition.
if not hasattr(socket, 'IP_ADD_SOURCE_MEMBERSHIP'):
	setattr(socket, 'IP_ADD_SOURCE_MEMBERSHIP', 39)

keepGoing = True
mgroup = None
port = None
msf = None
local_ip = "0.0.0.0"

def shutdown(sig, frame):
	global keepGoing
	keepGoing = False

def printUsage():
	print "Usage: %s -e mgroup:port [-s source] [-l localip]" % sys.argv[0]

try:
	opts, args =  getopt.getopt(sys.argv[1:], "e:s:l:h")
except getopt.GetoptError as e:
	print e
	printUsage();
	sys.exit()

for o,a in opts:
	if o == "-e":
		mgroup, port = a.split(':')
		mgroup = socket.gethostbyname(mgroup)
		port = int(port)
	if o == "-l":
		local_ip = socket.gethostbyname(a)
	if o == "-s":
		msf = socket.gethostbyname(a)
	if o == "-h":
		printUsage()
		sys.exit()

if mgroup is None or port is None:
	printUsage();
	sys.exit()


signal.signal(signal.SIGINT, shutdown)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((mgroup, port))
try:
	if msf is None:
		print "Trying out IGMPv2 subscription"
		s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(mgroup) + socket.inet_aton(local_ip))
	else:
		print "Trying out IGMPv3 subscription"
		s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_SOURCE_MEMBERSHIP, socket.inet_aton(mgroup) + socket.inet_aton(local_ip) + socket.inet_aton(msf))
	s.settimeout(4.0)
except:
	pass

while keepGoing:
	try:
		data, endpoint = s.recvfrom(1024)
		sess, seqno, nmsg = struct.unpack(">10sQH", data[:20])
		print endpoint[0], ">>> [%s, %lu, %d" % (sess, seqno, nmsg), base64.b64encode(data[20:]), "]"
	except:
		pass

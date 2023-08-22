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

def shutdown(sig, frame):
	global m
	m.stop()

def printUsage():
	print "Usage: %s -e mgroup:port [-s source] [-i interface]" % sys.argv[0]
	print "       %s -r host:port -S session [-n start[/count]]" % sys.argv[0]
	print "       %s -h" % sys.argv[0]

class MoldPrinter:
	@staticmethod
	def _handlePackets(buf, endpoint):
		ss, seqnum, nmsg = struct.unpack('>10sQH', buf[:20])
		print "Downstream Packet (endpoint=%s:%d) {" % endpoint
		print "\tSession = %s,\n\tSequence Number = %lu,\n\tMessage Count = %u," % (ss, seqnum, nmsg)
		x = buf[20:]
		while len(x) > 0:
			print "\tMessage Block {"
			msize, = struct.unpack('>H', x[:2])
			print "\t\tMessage Length = %d," % (msize,)
			print "\t\tMessage Data =", base64.b64encode(x[2:2+msize])
			print "\t}"
			x = x[2+msize:]
		print "}"
		return nmsg

class MoldStreamPrinter (MoldPrinter):
	def __init__(self, addr, msf, mif):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.settimeout(4.0)
		self.socket = s
		self._joinStream(addr, msf, mif)

	def run(self):
		self.keepGoing = True
		while self.keepGoing:
			try:
				data, endpoint = self.socket.recvfrom(1024)
				self._handlePackets(data, endpoint)
			except:
				pass

	def stop(self):
		self.keepGoing = False

	def _joinStream(self, addr, msf, mif):
		self.socket.bind(addr)
		try:
			if msf is None:
				print "Trying out IGMPv2 subscription"
				self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(addr[0]) + socket.inet_aton(mif))
			else:
				print "Trying out IGMPv3 subscription"
				self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_SOURCE_MEMBERSHIP, socket.inet_aton(addr[0]) + socket.inet_aton(mif) + socket.inet_aton(msf))
		except:
			pass

class MoldRecoveryPrinter (MoldPrinter):
	def __init__(self, addr, session, start, count):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.addr = addr
		self.session = session
		self.start = start
		self.count = count
		self.received = 0

	def run(self):
		self.keepGoing = True
		while self.count - self.received > 0 and self.keepGoing:
			self._requestPackets()
			data, endpoint = self.socket.recvfrom(2048)
			nmsg = self._handlePackets(data, endpoint)
			self.received = self.received + nmsg

	def stop(self):
		self.keepGoing = False

	def _requestPackets(self):
		x = struct.pack('>10sQH', self.session, self.start + self.received, self.count - self.received)
		self.socket.sendto(x, self.addr)
		

mgroup = None
host = None
port = None
msf = None
mif = "0.0.0.0"
start = 1
count = 10
session = None

try:
	opts, args =  getopt.getopt(sys.argv[1:], "e:s:i:r:S:n:h")
except getopt.GetoptError as e:
	print e
	printUsage()
	sys.exit()

for o,a in opts:
	if o == "-e":
		mgroup, port = a.split(':')
		mgroup = socket.gethostbyname(mgroup)
		port = int(port)
	if o == "-i":
		mif = socket.gethostbyname(a)
	if o == "-s":
		msf = socket.gethostbyname(a)
	if o == "-r":
		host, port = a.split(':')
		host = socket.gethostbyname(host)
		port = int(port)
	if o == "-S":
		session = a
	if o == "-n":
		try:
			start, count = a.split('/')
		except ValueError:
			start = a
		start = int(start)
		count = int(count)
	if o == "-h":
		printUsage()
		sys.exit()

if (mgroup is None and host is None) or port is None:
	printUsage()
	sys.exit()

if mgroup:
	m = MoldStreamPrinter((mgroup, port), msf, mif)
else:
	m = MoldRecoveryPrinter((host, port), session, start, count)

signal.signal(signal.SIGINT, shutdown)
m.run()

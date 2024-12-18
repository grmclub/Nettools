#!/usr/bin/env python

import os, sys, getopt
import errno, traceback

import SocketServer
import SimpleHTTPServer
import urllib


class MyProxy(SimpleHTTPServer.SimpleHttpRequestHandler):
	def do_GET(self):
		url=self.path[1:]
		self.send_response(200)
		self.end_headers()
		self.copyfile(urllib.urlopen(url), self.wfile)
		
PORT = 9090
httpd = SocketServer.ForkingTCPServer('',PORT), MyProxy)
print("Server open at port:%s " % str(PORT))
http.serve_forever()

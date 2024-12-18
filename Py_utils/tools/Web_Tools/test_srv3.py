#!/usr/bin/python2.6

import string,time
import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

import os
import getopt
import sys
import signal
import errno
import mimetypes
import base64
from daemon import *

class MyHandler(BaseHTTPRequestHandler):

    def _writeheaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._writeheaders()
        self.wfile.write("<Kill Switch>")
        self.wfile.write("Hello!! It's Day :" + str(time.localtime()[7]) + "  ")
        self.wfile.write(" in the year " + str(time.localtime()[0]))
        #self.wfile.write("""<HTML><HEAD><TITLE>Sample Page</TITLE></HEAD>
        #<BODY>This is a sample HTML page.</BODY></HTML>""")


    def do_POST(self):
        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        # Begin the response
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('Path: %s\n' % self.path)
        self.wfile.write('Form data:\n')

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                del file_data
                self.wfile.write('\tUploaded %s (%d bytes)\n' % (field,
                                                                 file_len))
            else:
                # Regular form value
                self.wfile.write('\t%s=%s\n' % (field, form[field].value))
        return

keepGoing = True

def shutdown(sig, frame):
	global keepGoing
	keepGoing = False

def print_usage():
    print('Usage: %s ' % sys.argv[0])
    print '''
    -c arg  Configuration file (eg. ./config.ini)
    -p arg  PidFile name for application
    -D      Don't run application as daemon
    -P arg  Server port
    -h      Print Help
    -v      Print version
    '''

class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass

def main():

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    daemonize = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:p:DP:v")
    except getopt.GetoptError as e:
        print e
        sys.exit(2)

    for o,a in opts:
        if o == "-c":
	        app_config = a
        elif o == "-p":
	        app_pidfile = a
        elif o == "-P":
	        app_port = int(a)
        elif o == "-D":
	        daemonize = False
        elif o == "-h":
	        print_usage()
	        sys.exit()
        elif o == "-v":
	        print("v0.1.1")
	        sys.exit()
        else:
            assert False, "unhandled option"


    pidfile = PidFile(app_pidfile)
    try:
        pidfile.open(0644)
    except DaemonAlreadyRunning as e:
        print "Daemon already running, pid: %d" % (e.otherpid,)
        sys.exit(2)
    except:
        print "Can not open or create pidfile"
        sys.exit(2)

    if daemonize:
        daemon(nochdir=True)

    pidfile.write()

    try:

        server = ThreadingServer(('',app_port), MyHandler)
        print 'Started RedEye server listening on port:', app_port;
        #server.serve_forever()
        global keepGoing
        while keepGoing:
            server.handle_request() 

    except KeyboardInterrupt:
        print 'Shutting down server..'
    
    except :
        print "keepGoing: ", keepGoing
        server.socket.close()

if __name__ == '__main__':
    main()

#!/usr/bin/python

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


class MyHandler(BaseHTTPRequestHandler):

    def _writeheaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._writeheaders()
        self.wfile.write("<Kill switch>")
        self.wfile.write("Hallo!! It's Day :" + str(time.localtime()[7]) + "  ")
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



def print_usage():
    sys.exit('Usage: %s <port>' % sys.argv[0])

class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass

def main():
    try:

        if len(sys.argv) < 2:
            print_usage()

        if sys.argv[1:]:
            port = int(sys.argv[1])
        else:
            port = 8080
        server = ThreadingServer(('',port), MyHandler)
        print 'Started RedEye server listening on port:', port;

        server.serve_forever()

    except KeyboardInterrupt:
        print 'Shutting down server..'
        server.socket.close()

if __name__ == '__main__':
    main()

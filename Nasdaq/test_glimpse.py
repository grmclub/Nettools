#!/usr/bin/env python
import errno
import getopt
import os
import socket
import select
import struct
import sys
import time
import traceback

class libSoup():

    def __init__(self, user, passwd, ip, port,seq_num=''):
        self.heartbeat = struct.pack('>Hc', 1, 'R')
        self.start_heartbeat = time.time()
        self.sock = ""

        self.ip     = ip
        self.port   = port
        self.user   = user
        self.passwd = passwd
        self.session_no  = ""
        self.recv_bufsize = 1024*5

        self.passwd = self.passwd.ljust(10,' ')
        self.session_no = self.session_no.rjust(10,' ')
        self.seq_num = seq_num.rjust(20,' ')


    def _send(self,data):
        self.sock.sendall(data)

    def recv_data(self):
        data = ""
        while True:
            buf = self.sock.recv(self.recv_bufsize)
            if not buf: break;
            data += buf
        return data


    def send_heartbeat(self):
        if ( (time.time()-self.start_heartbeat) >= 2):
            self._send(self.heartbeat)
            self.start_heartbeat = time.time()

    def connect(self):
        try:
            host = self.ip
            port = int(self.port)
            self.sock = socket.socket()
            self.stopFlag = False
            server_address = (host,port)
            self.sock.connect(server_address)
            print('Connected')
            self.soup_login()
            time.sleep(1)

        except Exception as e:
            print e
            print traceback.format_exc(sys.exc_info())
            sys.exit(1)

    def disconnect(self):
        try:
            self.sock.close()
            print('Disconnected')
        except:
            print('Error closing socket')

    def soup_login(self):
        try:
            login_message = struct.pack('>Hc6s10s10s20s', 47, 'L', self.user,
                                                                   self.passwd,
                                                                   self.session_no,
                                                                   self.seq_num)
            #print('Sending login request for %s' % self.user)
            #print(struct.unpack('>Hc6s10s10s20s', login_message))
            self._send(login_message)
            data = self.sock.recv(3)
            soup_header = struct.unpack('>Hc', data)
            if soup_header[1] =='A':
                data = self.sock.recv(soup_header[0])
                data = struct.unpack('>10s20s', data)
                print "Login Success session:" + data[0] + "seq no." + data[1]

            elif soup_header[1] =='J':
                data = self.sock.recv(soup_header[0])
                data = struct.unpack('>1s', data)
                print "Login Failed Rej Code:" + data[0]

            else:
                print "Login Failed unknown error"
                self.sock.close()
                sys.exit(3)

        except:
            print traceback.format_exc(sys.exc_info())
            sys.exit(1)

    def soup_logout(self):
        try:
            logout_message = struct.pack('>Hc', 1, 'O')
            self.sock._send(logout_message)
            print (self.recv_data())
        except:
            pass

    def process(self):
        try:
            inout = [self.sock]
            while 1:
                infds, outfds, errfds = select.select(inout, inout, [], 1)
                #if self.sock:
                #    self.send_heartbeat()
                if self.stopFlag:
                    break

                if len(infds) != 0:
                    buf = self.sock.recv(3)
                    if len(buf) != 0:
                       soup_header = struct.unpack('>Hc',buf)
                       self.unpackItch(soup_header)

        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            print("Error: %s\n" %str(err))
            sys.exit(2)

    def _output(self, transport_header, app_protocol_header, _data):
        print ("%s %s %s" % (transport_header, app_protocol_header, _data))


    def unpackItch(self, soup_header):
        try:
            header = ()
            data   = ()
            if (soup_header[1] == 'S'):       #Soup Sequenced packet
                raw_header = self.sock.recv(1)
                header = struct.unpack('c', raw_header)
                raw_data = self.sock.recv(soup_header[0]-2)

                if (header[0] == 'T'):        # Timestamp
                    data = struct.unpack('>I', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'S'):        # System Event
                    data = struct.unpack('>I4sc', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'L'):        # Price Tick Size
                    data = struct.unpack('>IIII', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'R'):        # Stock Directory
                    data = struct.unpack('>II12s4sIIIII', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'H'):        # Stock Trading Action
                    data = struct.unpack('>II4sc', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'Y'):        # SS Price Restriction Inidcator
                    data = struct.unpack('>II4sc', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'A'):        # Add Order
                    data = struct.unpack('>IQcII4sI', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'F'):        # Add Order With Attributes
                    data = struct.unpack('>IQcII4sI4sc', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'E'):        # Executed
                    data = struct.unpack('>IQIQ', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'D'):        # Delete
                    data = struct.unpack('>IQ', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'U'):        # Update
                    data = struct.unpack('>IQQII', raw_data)
                    self._output(soup_header, header, data)

                if (header[0] == 'G'):        # End of Snapshot
                    self.stopFlag = True
                    data = struct.unpack('>Q', raw_data)
                    self._output(soup_header, header, data)

                return (header + data)

        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            print("Error: %s\n" %str(err))
            sys.exit(2)

    def __del__(self):
        if self.sock:
            self.sock.close()


def printHelp():
    print """Usage: %s -f <filename>

    OPTIONS:
         -i  ip
         -p  port
         -U  user
         -P  login passw
         -h  Display this help message.
    """ % os.path.basename(__file__)  # sys.argv[0]

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:p:U:P:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        soup_ip    = ""
        soup_port  = ""
        soup_user  = ""
        soup_passw = ""
        for o,a in opts:
            if o == "-i":
                soup_ip = a

            if o == "-p":
                soup_port = a

            if o == "-U":
                soup_user = a

            if o == "-P":
                soup_passw = a

            if o == "-h":
                printHelp()
                sys.exit(0)

        #(self, user, passwd, ip, port,seq_num=''):
        soupconn = libSoup(soup_user, soup_passw, soup_ip, soup_port)
        soupconn.connect()
        soupconn.process()


    except Exception, err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)



if __name__ == "__main__":
    main()





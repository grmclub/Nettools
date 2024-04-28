#!/usr/bin/env python

import os,sys,getopt
import errno,traceback
import socket,select

class server:
    def __init__(self):
        self.CONNECTION_LIST = []
        self.RECV_BUFFER = 4096
        self.PORT = 5000
        self.BACKLOG = 10
        self.keeprunning = True

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", self.PORT))
        self.server_socket.listen(self.BACKLOG)
        self.CONNECTION_LIST.append(self.server_socket)

    def close(self):
        msg = "[Server] Shutting down...\n"
        print msg
        self.broadcast_data(self.server_socket, msg)
        self.keeprunning = False
        self.server_socket.close()

    def run(self):
        print "Server started on port " + str(self.PORT)
        while self.keeprunning:
            read_sockets,write_sockets,error_sockets = select.select(self.CONNECTION_LIST,[],[])
            for sock in read_sockets:
                if sock == self.server_socket: #New connection
                    sockfd, addr = self.server_socket.accept()
                    self.CONNECTION_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr
                    self.broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)

                else: #client message
                    try:
                        data = sock.recv(self.RECV_BUFFER)
                        if data:
                            self.broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)
                    except:
                        #self.broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                        print "Client (%s, %s) is offline" % addr
                        sock.close()
                        self.CONNECTION_LIST.remove(sock)
                        continue

    def broadcast_data (self, sock, message):
        for socket in self.CONNECTION_LIST:
            #Skip server socket,sending client
            if socket != self.server_socket and socket != sock :
                try :
                    socket.send(message)
                except :
                    # broken socket connection
                    socket.close()
                    self.CONNECTION_LIST.remove(socket)
                    continue

def main():
    chat_server = server()
    try:
        chat_server.run()
    except (KeyboardInterrupt, SystemExit):
        chat_server.close()
    except Exception, err:
        chat_server.close()
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()

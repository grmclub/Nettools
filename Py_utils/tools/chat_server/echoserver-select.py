#!/usr/bin/env python


import select
import socket
import sys

host = ''
port = 6000
backlog = 10
size    = 4096
server  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen(10)
input   = [server,sys.stdin]
running = True
print "Server started on port %d" % port
while running:
    inputready,outputready,exceptready = select.select(input,[],[])

    for s in inputready:

        if s == server:
            # handle the server socket
            client, address = server.accept()
            input.append(client)

        elif s == sys.stdin:
            # handle standard input
            junk = sys.stdin.readline()
            running = False

        else:
            # handle all other sockets
            data = s.recv(size)
            if data:
                s.send(data)
            else:
                s.close()
                input.remove(s)
server.close()

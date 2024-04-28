#!/usr/bin/env python


import socket, select

#broadcast message to all connected clients
def broadcast_data (sock, message):
	for socket in CONNECTION_LIST:
    	#Do not send the message to server socket and sending client
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				# broken socket connection
				socket.close()
				CONNECTION_LIST.remove(socket)

if __name__ == "__main__":
	
	# keep track of socket descriptors
	CONNECTION_LIST = []
	RECV_BUFFER = 4096
	PORT = 5000
	
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# this has no effect, why ?
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(("0.0.0.0", PORT))
	server_socket.listen(10)

	# Add to the list of readable connections
	CONNECTION_LIST.append(server_socket)

	print "Chat server started on port " + str(PORT)

	while 1:
		read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

		for sock in read_sockets:
			#New connection
			if sock == server_socket:
				sockfd, addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)
				print "Client (%s, %s) connected" % addr
				
				broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
			
			#Some incoming message from a client
			else:
				# Data recieved from client, process it
				try:
					#In Windows, sometimes when a TCP program closes abruptly,
					# a "Connection reset by peer" exception will be thrown
					data = sock.recv(RECV_BUFFER)
					if data:
						broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)                
				
				except:
					broadcast_data(sock, "Client (%s, %s) is offline" % addr)
					print "Client (%s, %s) is offline" % addr
					sock.close()
					CONNECTION_LIST.remove(sock)
					continue
	
	server_socket.close()
#ifndef CONNECT_H
#define CONNECT_H
#include <stdint.h>
#include <arpa/inet.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <netdb.h>
#include <errno.h>

#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <iostream>
#include <string>

#include "../utils/Log.h"

bool set_non_blocking(int, const bool);
ssize_t socket_read(int, char*, size_t);
ssize_t socket_write(int, const char*, size_t);

ssize_t socket_read_all(int, unsigned char* , size_t);
ssize_t socket_write_all(int, unsigned char*, size_t);
ssize_t socket_write_all(int, const std::string&, size_t);

int socket_connect(const char*, in_port_t);
//int socket_connect2(const char*, const char*);

const char* socket_getpeername(int, int*, char*, socklen_t);
const char* socket_getpeername(int, int*, char*, socklen_t);



#endif //CONNECT_H

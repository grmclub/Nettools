#include "connect.h"

bool set_non_blocking(int fd, const bool b)
{
    int opts;
    opts = fcntl(fd, F_GETFL);

    if (opts < 0) {
        return false;
    }
    if (b) {
        opts =(opts | O_NONBLOCK);
    }else{
        opts =(opts & ~O_NONBLOCK);
    }
    fcntl(fd, F_SETFL, opts);
    return true;
}

const char* socket_getpeername(int fd, int* port, char* buff, socklen_t size) {
    sockaddr_in address;
    socklen_t address_length = sizeof (address);
    if (getpeername(fd, reinterpret_cast<sockaddr*>(&address), &address_length) == -1)
        return NULL;
    if (port != NULL)
        *port = static_cast<int>(ntohs(address.sin_port));
    return inet_ntop(AF_INET, &address.sin_addr, buff, size);
}

const char* socket_getsockname(int fd, int* port, char* buff, socklen_t size) {
    sockaddr_in address;
    socklen_t address_length = sizeof (address);
    if (getsockname(fd, reinterpret_cast<sockaddr*>(&address), &address_length) == -1)
        return NULL;
    if (port != NULL)
        *port = static_cast<int>(ntohs(address.sin_port));
    return inet_ntop(AF_INET, &address.sin_addr, buff, size);
}

// On success, the number of bytes read is returned (zero indicates end of file). On error, -1 is returned.
ssize_t socket_read(int fd, char* buff, size_t size) {
	ssize_t n;
	while ((n = read(fd, buff, size)) == -1 && errno == EINTR)
    //while ((n = recv(fd, buff, size, 0)) == -1 && errno == EINTR)
		;
	return n;
}

// On success, the number of bytes written is returned (zero indicates nothing was written). On error, -1 is returned.
ssize_t socket_write(int fd, const char* buff, size_t size) {
	ssize_t n;
	while ((n = write(fd, buff, size)) == -1 && errno == EINTR)
    //while ((n = send(fd, buff, size, MSG_NOSIGNAL)) == -1 && errno == EINTR)
		;
	return n;
}

// On success, the number of bytes read is returned
//(zero indicates end of file).
//On error, -1 is returned.
ssize_t socket_read_all(int fd, unsigned char* buff, size_t size) {

    size_t i = 0;
    while (i < size) {
        ssize_t n = read(fd, &buff[i], size - i);
        if (n == -1) {
            if (errno == EINTR)
                continue;
            else if (errno == EWOULDBLOCK || errno == EAGAIN)
                return i;

            return n;
        }
        i += n;
    }
    return i;
}

ssize_t socket_write_all(int fd, unsigned char* buff, size_t size) {

    size_t i = 0;
    while (i < size) {
        ssize_t n = write(fd, &buff[i], size - i);
        if (n == -1) {

            if (errno == EINTR)
                continue;
            return n;
        }
        i += n;
    }
    return i;
}

ssize_t socket_write_all(int fd, const std::string& buff, size_t size) {

    size_t i = 0;
    while (i < size) {
        ssize_t n = socket_write(fd, &buff[i], size - i);
        if (n == -1) {

            if (errno == EINTR)
                continue;

            return n;
        }
        i += n;
    }
    return i;
}

int socket_connect(const char *host, in_port_t port) {
    struct hostent *hp;
    struct sockaddr_in addr;
    int on = 1, sock = -1;

    if ((hp = gethostbyname(host)) == NULL) {
        misc::appLog(misc::APP_LOG_NOTICE, "socket_connect: gethostbyname error...");
        return -1;
    }

    // copy address to sockaddr_in
    memcpy(&addr.sin_addr, hp->h_addr_list[0], hp->h_length);

    addr.sin_port = htons(port);
    addr.sin_family = AF_INET;

    sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
    setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, (const char *)&on, sizeof(int));

    if (sock == -1) {
        misc::appLog(misc::APP_LOG_NOTICE, "socket_connect: socket creation failed...");
    }

    if (connect(sock, (struct sockaddr *)&addr, sizeof(struct sockaddr_in)) == -1) {
        misc::appLog(misc::APP_LOG_NOTICE, "socket_connect: connect error...");
        return -1;
    }

    return sock;
}
/*
//Newer struct syntax
int socket_connect2(const char* host, const char* service) {
	int fd = socket(PF_INET, SOCK_STREAM, 0);
	if (fd == -1)
		return -1;

	addrinfo* address;
	if (getaddrinfo(host, service, NULL, &address) == -1)
		return -1;

	const bool PRINT_ADDRINFO = false;
	if (PRINT_ADDRINFO) {
		for (const addrinfo* p = address; p != NULL; p = p->ai_next) {
			char hostname[NI_MAXHOST] = "";
			if (getnameinfo(address->ai_addr, address->ai_addrlen, hostname, NI_MAXHOST, NULL, 0, 0) == -1)
				continue;
			(void) hostname;
			(void) ntohs(reinterpret_cast<sockaddr_in*>(p->ai_addr)->sin_port);
		}
	}

	socklen_t address_length = sizeof (*address);
	while (connect(fd, reinterpret_cast<sockaddr*>(address->ai_addr), address_length) == -1) {
		if (errno == EINTR)
			continue;
		freeaddrinfo(address);
		return -1;
	}
	freeaddrinfo(address);

	return fd;
}

*/


#include <arpa/inet.h>
#include <netinet/tcp.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdint.h>
#include <iostream>
#include <cstring>
#include <ctime>
#include <poll.h>
#include <cassert>
#include <cerrno>

#define USER_LEN        6
#define PASSWORD_LEN    10
#define SESSION_LEN     10
#define SEQUENCE_LEN    20

// send a heartbeat ever n milliseconds
#define HEARTBEAT_INTERVAL  1000
#define FILENAME_LEN        1024

#pragma pack(push, 1)
struct LengthType {
    uint16_t    packetLength_;
    char        packetType_;
};

struct LoginPacket {
    LengthType      header_;
    char            user_[USER_LEN];
    char            password_[PASSWORD_LEN];
    char            session_[SESSION_LEN];
    char            sequence_[SEQUENCE_LEN];
};

union ClientPackets {
    LoginPacket login_;
    LengthType  logout_;
    LengthType  heartbeat_;
};

// data should really be a union of itch messages
#define DATA_LEN    1024
struct SequencedPacket {
    LengthType  header_;
    char        data_[1024];
};

struct LoginAcceptedPacket {
    LengthType  header_;
    char        session_[SESSION_LEN];
    char        sequence_[SEQUENCE_LEN];

};

struct LoginRejectedPacket {
    LengthType  header_;
    char            reason_;
};

union ServerPackets {
    LengthType          header_;
    LengthType          heartbeat_;
    LengthType          session_;
    SequencedPacket     sequence_;
    LoginAcceptedPacket login_accept_;
    LoginRejectedPacket login_reject_;
};
#pragma pack(pop)

using namespace std;

int serverConnect(struct sockaddr_in *);

int serverConnect(struct sockaddr_in * server) {
    int sock_fd = socket(PF_INET, SOCK_STREAM, 0);

    if (sock_fd == -1) {
        cerr << "Could not create socket" << endl;
        return -1;
    }
    int a = 1;
    setsockopt(sock_fd, IPPROTO_TCP, TCP_NODELAY, &a, 4);

    if (connect(sock_fd, (struct sockaddr *) server, sizeof(struct sockaddr_in)) == -1) {
        cerr << strerror(errno) << endl;
        return -1;
    }
    return sock_fd;
}

bool serverLogon(int sock_fd, char * session, int sequence, char const * user, char const * password)
    LoginPacket login;
    ServerPackets server_incoming;
    char sequence_buff[SEQUENCE_LEN+1];

    memset(sequence_buff, ' ', sizeof(sequence_buff));
    snprintf(sequence_buff, SEQUENCE_LEN+1, "%*d", SEQUENCE_LEN, sequence);

    // handle padding of text fields
    memset(&login, ' ', sizeof(login));

    login.header_.packetLength_ = htons(sizeof(LoginPacket) - sizeof(uint16_t));
    login.header_.packetType_ = 'L';

    memcpy(login.user_, user, USER_LEN);
    memcpy(login.password_, password, PASSWORD_LEN);
    memcpy(login.session_, session, SESSION_LEN);
    memcpy(login.sequence_, sequence_buff, SEQUENCE_LEN);

    write(sock_fd, &login, sizeof(login));

    read(sock_fd, &server_incoming, sizeof(uint16_t));
    server_incoming.header_.packetLength_ = ntohs(server_incoming.header_.packetLength_);
    read(sock_fd, (char *)(&server_incoming) + sizeof(uint16_t), server_incoming.header_.packetLength
    switch (server_incoming.header_.packetType_) {
        case 'A':
            cerr << "Login accepted - session: " << string(server_incoming.login_accept_.session_, SE
            cerr << " Sequence: " << string(server_incoming.login_accept_.sequence_, SEQUENCE_LEN) <<
            memcpy(session, server_incoming.login_accept_.session_, SESSION_LEN);
            return true;
        case 'J':
            cerr << "Login rejected with rejection code: " << server_incoming.login_reject_.reason_ <
            break;
        default:
            cerr << "Unknown message type: " << server_incoming.header_.packetType_ << endl;
    }
    return false;
}

int main(int argc, char **argv) {
    struct sockaddr_in serv_addr;
    uint16_t server_port;
    uint32_t sequence_number;
    char     session[SESSION_LEN];
    char     user[USER_LEN];
    char     password[PASSWORD_LEN];
    int      sock_fd;
    int      port;

    sequence_number = 1;
    memset(session, ' ', sizeof(session));
    memset(user, ' ', sizeof(user));
    memset(password, ' ', sizeof(password));

    if (argc < 4 || argc > 7) {
        cerr << "Usage: " << argv[0] << " <Server IP> <Port> <User> <Password> (Session) (Sequence)"
        return 1;
    }

    int user_len = strlen(argv[3]);
    if (user_len > USER_LEN) {
        cerr << "User string too long" << endl;
        return 1;
    }
    memcpy(user, argv[3], user_len);

    int password_len = strlen(argv[4]);
    if (password_len > PASSWORD_LEN) {
        cerr << "Password string too long" << endl;
        return 1;
    }
    memcpy(password, argv[4], password_len);

    if (argc >= 6) {
        int session_len = strlen(argv[5]);
        if (session_len > SESSION_LEN) {
            cerr << "Session string too long" << endl;
            return 1;
        }
        memcpy(session, argv[5], SESSION_LEN);
    }
    
    if (argc == 7) {
        sequence_number = atoi(argv[6]);
        if (sequence_number < 0) {
            cerr << "Sequence number must be >= 0" << endl;
            return 1;
        }
    }

    if (!inet_aton(argv[1], &serv_addr.sin_addr)) {
        cerr << "Bad server IP" << endl;
        return 1;
    }

    port = atoi(argv[2]);
    server_port = port;
    if (port <= 0 || server_port != port) {
        cerr << "Bad server port" << endl;
        return 1;
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(server_port);

    if ((sock_fd = serverConnect(&serv_addr)) == -1)
        return 1;

    if (!serverLogon(sock_fd, session, sequence_number, user, password))
        return 1;

    ServerPackets server_incoming;
    LengthType heartbeat;
    heartbeat.packetType_ = 'R';
    heartbeat.packetLength_ = htons(1);

    struct pollfd poll_data;
    poll_data.fd = sock_fd;
    poll_data.events = POLLIN | POLLERR;
    poll_data.revents = 0;
    int rv;
    clock_t cpu_time = clock();
    long int time_difference;

    char output_file[FILENAME_LEN];
    snprintf(output_file, FILENAME_LEN, "ITCH-%d.log",atoi(string(session, SESSION_LEN).c_str()));
    FILE * output_fd = fopen(output_file, "w");
    if (output_fd == NULL) {
        cerr << strerror(errno) << endl;
        return 1;
    }

    while ((rv = poll(&poll_data, 1, HEARTBEAT_INTERVAL)) != -1) {
        // quickly work out if we need to send a heartbeat packet
        time_difference = clock() - cpu_time;
        if (!rv || time_difference < 0 || ((time_difference * 1000) / CLOCKS_PER_SEC > HEARTBEAT_INTERVAL
            write(sock_fd, &heartbeat, sizeof(heartbeat));
            cpu_time = clock();
        }

        /* data is waiting */
        if (poll_data.revents & POLLIN) {
            read(sock_fd, &server_incoming, sizeof(uint16_t));
            server_incoming.header_.packetLength_ = ntohs(server_incoming.header_.packetLength_);
            read(sock_fd, (char *)(&server_incoming) + sizeof(uint16_t), server_incoming.header_.pack
            // sequenced data packet from server - write the payload to a file
            if (server_incoming.header_.packetType_ == 'S') {
                uint16_t itch_size = htons(server_incoming.header_.packetLength_-1);
                fwrite(&itch_size, sizeof(uint16_t), 1, output_fd);
                fwrite(server_incoming.sequence_.data_, ntohs(itch_size), 1, output_fd);
                sequence_number++;
            }
        }
        if (poll_data.revents & POLLERR) {
            cerr << "HANDLE ERROR!" << endl;
            // handle error
            break;
        }
        poll_data.fd = sock_fd;
        poll_data.events = POLLIN | POLLERR;
        poll_data.revents = 0;
    }
    return 0;
}    

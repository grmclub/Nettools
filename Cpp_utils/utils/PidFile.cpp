#include "PidFile.h"

#include <sys/file.h>
#include <unistd.h>

#include <cerrno>
#include <cstdio>
#include <cstdlib>

namespace {

const int READ_ATTEMPTS_MAX = 3;

} // namespace

namespace misc {

PidFile::PidFile(const char* pidFilename)
	: m_pidFilename(pidFilename)
	, m_fd(-1)
	, m_opened(false) {
}

PidFile::~PidFile() {
	remove();
}

void PidFile::open(int mode) {
	int fd = ::open(m_pidFilename.c_str(), O_WRONLY | O_CREAT, mode);
	if (fd == -1)
		throw IOError(m_pidFilename);
	try {
		if (flock(fd, LOCK_EX | LOCK_NB) == -1) {
			if (errno != EWOULDBLOCK)
				throw IOError();
			for (int nattempts = 0; nattempts < READ_ATTEMPTS_MAX; ++nattempts) {
				pid_t other;
				if (read(m_pidFilename.c_str(), other))
					throw DaemonAlreadyRunning(other);
				usleep(5000);
			}
			throw TimeoutError("Timeout");
		}
		if (ftruncate(fd, 0) == -1)
			throw IOError();
	}
	catch (...) {
		::close(fd);
		throw;
	}
	m_fd = fd;
	m_opened = true;
}

bool PidFile::read(const char* pidFilename, pid_t& pid) {
	int fd = ::open(pidFilename, O_RDONLY);
	if (fd == -1)
		throw IOError();
	char buf[32];
	int n = ::read(fd, buf, sizeof (buf) - 1);
	int error = errno;
	::close(fd);
	if (n == -1)
		throw IOError(error);
	if (n == 0)
		return false;
	buf[n] = 0;
	char* endp;
	pid = strtol(buf, &endp, 10);
	if (endp != buf + n)
		throw InvalidPidFile("PID is not a number");
	return true;
}

void PidFile::write() {
	if (ftruncate(m_fd, 0) == -1)
		throw IOError();
	char buf[32];
	int n = snprintf(buf, sizeof (buf), "%d", getpid());
	if (pwrite(m_fd, buf, n, 0) == -1)
		throw IOError();
}

void PidFile::close() {
	if (!m_opened)
		return;
	::close(m_fd);
	m_fd = -1;
	m_opened = false;
}

void PidFile::remove() {
	if (!m_opened)
		return;
	::close(m_fd);
	unlink(m_pidFilename.c_str());
	m_fd = -1;
	m_opened = false;
}

} // namespace misc

#ifndef MISC_PIDFILE_H
#define MISC_PIDFILE_H

#include <sys/types.h>
#include <string>

#include "Exception.h"

namespace misc {

class DaemonAlreadyRunning : public Exception {
public:
	explicit DaemonAlreadyRunning(pid_t other) throw ()
		: m_other(other) {
	}

	pid_t pid() const {
		return m_other;
	}

private:
	pid_t m_other;
};

class InvalidPidFile : public Exception {
public:
	explicit InvalidPidFile(const char* what) throw ()
		: Exception(what) {
	}

	explicit InvalidPidFile(const std::string& what) throw ()
		: Exception(what) {
	}
};

class PidFile {
public:
	explicit PidFile(const char*);
	~PidFile();

	void open(int);
	static bool read(const char*, pid_t&);
	void write();
	void close();
	void remove();

private:
	std::string m_pidFilename;
	int m_fd;
	bool m_opened;
};

} // namespace misc

#endif // MISC_PIDFILE_H

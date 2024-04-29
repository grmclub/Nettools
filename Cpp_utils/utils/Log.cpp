#include "Log.h"

#include <sys/time.h>

#include <mutex>

#include "Exception.h"

namespace misc {

int debug;

} // namespace misc

namespace {

void screenLogger(int, const char*, va_list);
const char* toString(int);
misc::app_logger_t logger = &screenLogger;
std::mutex mtx;

} // namespace

namespace misc {

app_logger_t appSetLogger(app_logger_t newLogger)
{
	app_logger_t oldLogger = logger;
	logger = newLogger;
	return oldLogger;
}

void appLog(int priority, const char* fmt, ...)
{
	if (logger == NULL)
		return;
	va_list ap;
	va_start(ap, fmt);
	logger(priority, fmt, ap);
	va_end(ap);
}

} // namespace misc

namespace {

void screenLogger(int priority, const char* fmt, va_list ap)
{
	timeval now;
	gettimeofday(&now, NULL);
	std::lock_guard<std::mutex> lk(mtx);
	fprintf(stderr, "%ld.%06ld %s: ", now.tv_sec, now.tv_usec, toString(priority));
	vfprintf(stderr, fmt, ap);
	fputc('\n', stderr);
}

const char* toString(int priority)
{
	switch (priority) {
	case misc::APP_LOG_EMERG:
		return "EMERG";
	case misc::APP_LOG_CRIT:
		return "CRIT";
	case misc::APP_LOG_ERR:
		return "ERR";
	case misc::APP_LOG_NOTICE:
		return "NOTICE";
	case misc::APP_LOG_INFO:
		return "INFO";
	case misc::APP_LOG_DEBUG:
		return "DEBUG";
	default:
		break;
	}
	throw misc::InvalidArgument("Invalid argument");
}

} // namespace

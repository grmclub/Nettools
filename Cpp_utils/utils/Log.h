#ifndef MISC_LOG_H
#define MISC_LOG_H

#include <cstdarg>
#include <cstdio>

namespace misc {

enum
{
	APP_LOG_EMERG,
	APP_LOG_CRIT,
	APP_LOG_ERR,
	APP_LOG_NOTICE,
	APP_LOG_INFO,
	APP_LOG_DEBUG
};

extern int debug;
typedef void (* app_logger_t)(int, const char*, va_list);
app_logger_t appSetLogger(app_logger_t);
void appLog(int, const char* fmt, ...) __attribute__ ((__format__ (__printf__, 2, 3)));

template <typename T>
	class LogSourceImpl
	{
	protected:
		void appLog(int priority, const char* fmt, ...) const
		{
			va_list ap;
			va_start(ap, fmt);
			char message[BUFSIZ];
			vsnprintf(message, sizeof (message), fmt, ap);
			va_end(ap);
			const T* o = static_cast<const T*>(this);
			misc::appLog(priority, "%s: %s", o->appLogId(), message);
		}
	};

} // namespace misc

#define APP_DEBUG(level, ...) do { if (misc::debug >= (level)) misc::appLog(misc::APP_LOG_DEBUG, __VA_ARGS__); } while (0)
#define APP_DEBUG_BEGIN(level) if (misc::debug >= (level)) {
#define APP_DEBUG_END() }

#endif // MISC_LOG_H

#include "form.h"

#include <cstdarg>
#include <cstdio>
#include <utility>

namespace misc {

std::string form(const char* fmt, ...)
{
	std::string str(81, char()); // Try default terminal width (80 chars + null).
	va_list ap;
	va_start(ap, fmt);
	int n = vsnprintf(&str[0], str.size(), fmt, ap);
	va_end(ap);
	if (n >= (int) str.size()) {
		str.resize(n + 1);
		va_start(ap, fmt);
		vsnprintf(&str[0], str.size(), fmt, ap);
		va_end(ap);
	}
	str.resize(n);
	return std::move(str);
}

} // namespace misc

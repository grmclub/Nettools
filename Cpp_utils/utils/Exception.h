#ifndef MISC_EXCEPTION_H
#define MISC_EXCEPTION_H

#include <cerrno>
#include <cstring>
#include <string>

#include "form.h"

namespace misc {

class Exception
{
public:
	explicit Exception(const char* what) throw ()
		: m_what(what)
	{}

	explicit Exception(const std::string& what) throw ()
		: m_what(what)
	{}

	virtual ~Exception()
	{}

	const char* what() const
	{ return m_what.c_str(); }

protected:
	Exception() throw ()
	{}

private:
	std::string m_what;
};

class LogicError : public Exception
{
public:
	explicit LogicError(const char* what) throw ()
		: Exception(what)
	{}

	explicit LogicError(const std::string& what) throw ()
		: Exception(what)
	{}
};

class DomainError : public Exception
{
public:
	explicit DomainError(const char* what) throw ()
		: Exception(what)
	{}

	explicit DomainError(const std::string& what) throw ()
		: Exception(what)
	{}
};

class InvalidArgument : public Exception
{
public:
	explicit InvalidArgument(const char* what) throw ()
		: Exception(what)
	{}

	explicit InvalidArgument(const std::string& what) throw ()
		: Exception(what)
	{}
};

class InternalError : public Exception
{
public:
	explicit InternalError(const char* what) throw ()
		: Exception(what)
	{}

	explicit InternalError(const std::string& what) throw ()
		: Exception(what)
	{}
};

class OptionError : public Exception
{
public:
	explicit OptionError(const char* what) throw ()
		: Exception(what)
	{}

	explicit OptionError(const std::string& what) throw ()
		: Exception(what)
	{}
};

class IllegalOption : public OptionError
{
public:
	explicit IllegalOption(int opt) throw ()
		: OptionError(form("Illegal option -%c", opt))
	{}
};

class InvalidOption : public OptionError
{
public:
	explicit InvalidOption(int opt) throw ()
		: OptionError(form("Option -%c requires an argument", opt))
	{}

	InvalidOption(int opt, const char* what) throw ()
		: OptionError(form("Option -%c has invalid value (%s)", opt, what))
	{}

	InvalidOption(int opt, const std::string& what) throw ()
		: OptionError(form("Option -%c has invalid value (%s)", opt, what.c_str()))
	{}
};

class IOError : public Exception
{
public:
	explicit IOError(int error = errno) throw ()
		: Exception(strerror(error))
		, m_error(error)
	{}

	explicit IOError(const char* filename, int error = errno) throw ()
		: Exception(strerror(error))
		, m_error(error)
		, m_filename(filename)
	{}

	explicit IOError(const std::string& filename, int error = errno) throw ()
		: Exception(strerror(error))
		, m_error(error)
		, m_filename(filename)
	{}

	int error() const
	{ return m_error; }

	const std::string& filename() const
	{ return m_filename; }

private:
	int m_error;
	std::string m_filename;
};

class TimeoutError : public Exception
{
public:
	explicit TimeoutError(const char* what) throw ()
		: Exception(what)
	{}

	explicit TimeoutError(const std::string& what) throw ()
		: Exception(what)
	{}
};

} // namespace misc

#endif // MISC_EXCEPTION_H

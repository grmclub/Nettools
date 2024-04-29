#ifndef PLIST_PLIST_H
#define PLIST_PLIST_H

#include <expat.h>
#include <sys/types.h>

#include <cstddef>
#include <istream>
#include <map>
#include <stack>
#include <string>
#include <vector>

#include "Exception.h"

namespace plist {

class Error : public misc::Exception
{
public:
	explicit Error(const char* what) throw () : Exception(what) {}
	explicit Error(const std::string& what) throw () : Exception(what) {}
};

class ParseError : public Error
{
public:
	ParseError(int line, XML_Error error) throw () : Error(XML_ErrorString(error)), _errorCode(error), _lineNumber(line) {}

	XML_Error errorCode() const { return _errorCode; }
	int lineNumber() const { return _lineNumber; }

private:
	XML_Error _errorCode;
	int _lineNumber;
};

class FormatError : public Error
{
public:
	FormatError(int line, const char* what) throw () : Error(what), _lineNumber(line) {}
	FormatError(int line, const std::string& what) throw () : Error(what), _lineNumber(line) {}

	int lineNumber() const { return _lineNumber; }

private:
	int _lineNumber;
};

class KeyError : public Error
{
public:
	KeyError() throw () : Error("Key error") {}
};

class IndexError : public Error
{
public:
	IndexError() throw () : Error("Index error") {}
};

class TypeError : public Error
{
public:
	TypeError() throw () : Error("Type error") {}
};

class Dict;
class Array;

class Element
{
public:
	virtual ~Element() {}

	virtual Element& operator [](const char*) const { throw TypeError(); }
	virtual Element& operator [](size_t) const { throw TypeError(); }
	virtual const Dict& asDict() const { throw TypeError(); }
	virtual Dict& asDict() { throw TypeError(); }
	virtual const Array& asArray() const { throw TypeError(); }
	virtual Array& asArray() { throw TypeError(); }
	virtual std::string asString() const { throw TypeError(); }
	virtual bool asBool() const { throw TypeError(); }
	virtual long asInteger() const { throw TypeError(); }
	virtual double asReal() const { throw TypeError(); }
	virtual const void* asData(void*, size_t&) const { throw Error("Not implemented"); }
	virtual time_t asDate() const { throw Error("Not implemented"); }
};

class Plist : public Element
{
public:
	Plist() : _root(NULL) {}
	explicit Plist(Element* root) : _root(root) {}
	~Plist() { delete _root; }

	Plist(const Plist&) = delete;
	Plist& operator =(const Plist&) = delete;

	Plist(Plist&&);
	Plist& operator =(Plist&&);

	Element& operator [](const char*) const;
	Element& operator [](size_t) const;
	const Dict& asDict() const;
	Dict& asDict();
	const Array& asArray() const;
	Array& asArray();
	std::string asString() const;
	bool asBool() const;
	long asInteger() const;
	double asReal() const;
	const void* asData(void*, size_t&) const;
	time_t asDate() const;

private:
	Element* _root;
};

class Cont : public Element
{
public:
	virtual void insert(const char*, Element*) { throw TypeError(); }
	virtual void append(Element*) { throw TypeError(); }
	virtual size_t size() const = 0;
};

class Dict : public Cont
{
public:
	virtual ~Dict() { for (auto i = _dict.begin(); i != _dict.end(); ++i) delete i->second; }

	// Element
	virtual Element& operator [](const char*) const;
	virtual Dict& asDict() { return *this; }
	virtual const Dict& asDict() const { return *this; }

	// Cont
	virtual void insert(const char* key, Element* element) { _dict[key] = element; }
	virtual size_t size() const { return _dict.size(); }

	std::string getString(const char* key) const { return (*this)[key].asString(); }
	bool getBool(const char* key) const { return (*this)[key].asBool(); }
	long getInteger(const char* key) const { return (*this)[key].asInteger(); }
	double getReal(const char* key) const { return (*this)[key].asReal(); }

private:
	std::map<std::string, Element*> _dict;
};

class Array : public Cont
{
public:
	virtual ~Array() { for (auto i = _array.begin(); i != _array.end(); ++i) delete *i; }

	// Element
	virtual Element& operator [](size_t) const;
	virtual const Array& asArray() const { return *this; }
	virtual Array& asArray() { return *this; }

	// Cont
	virtual void append(Element* element) { _array.push_back(element); }
	virtual size_t size() const { return _array.size(); }

	std::string getString(size_t i) const { return (*this)[i].asString(); }
	bool getBool(size_t i) const { return (*this)[i].asBool(); }
	long getInteger(size_t i) const { return (*this)[i].asInteger(); }
	double getReal(size_t i) const { return (*this)[i].asReal(); }

private:
	std::vector<Element*> _array;
};

class StringValue : public Element
{
public:
	explicit StringValue(const std::string& value) : _value(value) {}

	// Element
	virtual std::string asString() const { return _value; }

private:
	std::string _value;
};

class BoolValue : public Element
{
public:
	explicit BoolValue(bool value) : _value(value) {}

	// Element
	virtual bool asBool() const { return _value; }

private:
	bool _value;
};

class IntegerValue : public Element
{
public:
	explicit IntegerValue(long value) : _value(value) {}
	explicit IntegerValue(const char*);

	// Element
	virtual long asInteger() const { return _value; }

private:
	long _value;
};

class RealValue : public Element
{
public:
	explicit RealValue(double value) : _value(value) {}
	explicit RealValue(const char*);

	// Element
	virtual double asReal() const { return _value; }

private:
	double _value;
};

class PlistParser
{
public:
	PlistParser() { _parser = XML_ParserCreate(NULL); }
	~PlistParser() { XML_ParserFree(_parser); }

	PlistParser(const PlistParser&) = delete;
	PlistParser& operator =(const PlistParser&) = delete;

	Plist parseFile(const char*);
	Plist parseFile(const std::string& filename) { return parseFile(filename.c_str()); }
	Plist parseStream(std::istream&);

private:
	XML_Parser _parser;
	std::string _cur_key;
	std::string _cur_data;
	std::stack<Cont*> _stack;
	Element* _root;

	void resetParser();
	XML_Error errorCode() const { return XML_GetErrorCode(_parser); }
	const char* error(XML_Error = XML_ERROR_NONE) const;
	int lineNumber() const { return XML_GetCurrentLineNumber(_parser); }
	void addElement(Element*);
	void pushContainer(Cont* cont) { _stack.push(cont); }
	void popContainer() { _stack.pop(); }

	static void XMLCALL startElement(void* userData, const char* name, const char** attr)
		{ reinterpret_cast<PlistParser*>(userData)->startElement(name, attr); }
	void startElement(const char*, const char**);

	static void XMLCALL endElement(void* userData, const char* name)
		{ reinterpret_cast<PlistParser*>(userData)->endElement(name); }
	void endElement(const char*);

	static void XMLCALL characterData(void* userData, const XML_Char* content, int len)
		{ reinterpret_cast<PlistParser*>(userData)->characterData(content, len); }
	void characterData(const XML_Char* content, int len) { _cur_data.append(content, len); }
};

} // namespace plist

#endif // PLIST_PLIST_H

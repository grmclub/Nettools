#include "Plist.h"

#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <functional>
#include <ios>
#include <utility>

#include "Finally.h"

namespace {

inline void std_ios_exceptions(std::istream& is, std::ios_base::iostate except)
{
	is.exceptions(except);
}

} // namespace

namespace plist {

Plist::Plist(Plist&& other)
{
	_root = other._root;
	other._root = NULL;
}

Plist& Plist::operator =(Plist&& right)
{
	delete _root;
	_root = right._root;
	right._root = NULL;
	return *this;
}

Element& Plist::operator [](const char* key) const
{
	if (_root == NULL)
		throw TypeError();
	return (*_root)[key];
}

Element& Plist::operator [](size_t i) const
{
	if (_root == NULL)
		throw TypeError();
	return (*_root)[i];
}

const Dict& Plist::asDict() const
{
	if (_root == NULL)
		throw TypeError();
	return _root->asDict();
}

Dict& Plist::asDict()
{
	if (_root == NULL)
		throw TypeError();
	return _root->asDict();
}

const Array& Plist::asArray() const
{
	if (_root == NULL)
		throw TypeError();
	return _root->asArray();
}

Array& Plist::asArray()
{
	if (_root == NULL)
		throw TypeError();
	return _root->asArray();
}

std::string Plist::asString() const
{
	if (_root == NULL)
		throw TypeError();
	return _root->asString();
}

bool Plist::asBool() const
{
	if (_root == NULL)
		throw TypeError();
	return _root->asBool();
}

long Plist::asInteger() const
{
	if (_root == NULL)
		throw TypeError();
	return _root->asInteger();
}

double Plist::asReal() const
{
	if (_root == NULL)
		throw TypeError();
	return _root->asReal();
}

const void* Plist::asData(void* data, size_t& len) const
{
	if (_root == NULL)
		throw TypeError();
	return _root->asData(data, len);
}

time_t Plist::asDate() const
{
	if (_root == NULL)
		throw TypeError();
	return _root->asDate();
}

Element& Dict::operator [](const char* key) const
{
	auto i = _dict.find(key);
	if (i == _dict.end())
		throw KeyError();
	return *i->second;
}

Element& Array::operator [](size_t i) const
{
	if (i >= _array.size())
		throw IndexError();
	return *_array[i];
}

IntegerValue::IntegerValue(const char* value)
{
	errno = 0;
	char* endptr;
	_value = strtol(value, &endptr, 10);
	if (endptr == value || *endptr != '\0' || errno == ERANGE)
		throw TypeError();
}

RealValue::RealValue(const char* value)
{
	errno = 0;
	char* endptr;
	_value = strtod(value, &endptr);
	if (endptr == value || *endptr != '\0' || errno == ERANGE)
		throw TypeError();
}

Plist PlistParser::parseFile(const char* filename)
{
	std::ifstream ifs(filename);
	if (!ifs)
		throw Error(std::string("Can not open file: ") + filename);
	return parseStream(ifs);
}

Plist PlistParser::parseStream(std::istream& is)
{
	std::ios_base::iostate except = is.exceptions();
	is.exceptions(std::istream::failbit | std::istream::badbit);
	misc::Finally restore(&std_ios_exceptions, std::ref(is), except);
	resetParser();
	for (bool done = false; !done;) {
		char buf[BUFSIZ];
		size_t len = is.readsome(buf, sizeof (buf));
		done = len < sizeof (buf);
		if (XML_Parse(_parser, buf, len, done) == XML_STATUS_ERROR) {
			delete _root;
			_root = NULL;
			throw ParseError(lineNumber(), errorCode());
		}
	}
	Plist pl(_root);
	_root = NULL;
	return std::move(pl);
}

void PlistParser::resetParser()
{
	XML_ParserReset(_parser, NULL);
	XML_SetUserData(_parser, this);
	XML_SetElementHandler(_parser, &this->startElement, &this->endElement);
	XML_SetCharacterDataHandler(_parser, &this->characterData);
	_root = NULL;
	_cur_key.clear();
	_cur_data.clear();
}

const char* PlistParser::error(XML_Error error) const
{
	if (error == XML_ERROR_NONE)
		error = errorCode();
	return XML_ErrorString(error);
}

void PlistParser::addElement(Element* element)
{
	if (_stack.empty()) {
		if (_root != NULL)
			throw FormatError(lineNumber(), "Multiple root elements");
		_root = element;
		return;
	}
	if (!_cur_key.empty()) {
		_stack.top()->insert(_cur_key.c_str(), element);
		_cur_key.clear();
	}
	else {
		_stack.top()->append(element);
	}
}

void PlistParser::startElement(const char* name, const char**)
{
	_cur_data.clear();
	if (strcmp(name, "dict") == 0) {
		Dict* dict = new Dict();
		addElement(dict);
		pushContainer(dict);
		return;
	}
	if (strcmp(name, "array") == 0) {
		Array* array = new Array();
		addElement(array);
		pushContainer(array);
		return;
	}
}

void PlistParser::endElement(const char* name)
{
	if (strcmp(name, "dict") == 0 || strcmp(name, "array") == 0) {
		popContainer();
		return;
	}
	if (strcmp(name, "key") == 0) {
		_cur_key = _cur_data;
		return;
	}
	if (strcmp(name, "string") == 0) {
		addElement(new StringValue(_cur_data));
		return;
	}
	if (strcmp(name, "true") == 0) {
		addElement(new BoolValue(true));
		return;
	}
	if (strcmp(name, "false") == 0) {
		addElement(new BoolValue(false));
		return;
	}
	if (strcmp(name, "integer") == 0) {
		addElement(new IntegerValue(_cur_data.c_str()));
		return;
	}
	if (strcmp(name, "real") == 0) {
		addElement(new RealValue(_cur_data.c_str()));
		return;
	}
}

} // namespace plist

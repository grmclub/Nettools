#include <iostream>
#include <fstream>
#include <cstdint>
#include <cassert>
#include <cstring>
#include <map>
#include <list>
#include <arpa/inet.h>
#include <endian.h>

#define ntohll(x) be64toh(x)
#define LEN_BOARD 4
#pragma pack(push, 1)
struct ADD_TAG {
	char type_;
	std::uint32_t timestamp_;
	std::uint64_t orderNo_;
	char verb_;
	std::uint32_t quantity_;
	std::uint32_t orderbook_;
	char board_[LEN_BOARD];
	std::uint32_t price_;
	void ntoh();
};

struct REPLACE_TAG {
	char type_;
	std::uint32_t timestamp_;
	std::uint64_t origOrderNo_;
	std::uint64_t orderNo_;
	std::uint32_t quantity_;
	std::uint32_t price_;
	void ntoh();
};

struct CANCEL_TAG {
	char type_;
	std::uint32_t timestamp_;
	std::uint64_t orderNo_;
	void ntoh();
};

struct EXECUTE_TAG {
	char type_;
	std::uint32_t timestamp_;
	std::uint64_t orderNo_;
	std::uint32_t quantity_;
	std::uint64_t matchNo_;
	void ntoh();
};

struct QUOTE_TAG {
	char type_;
	std::uint32_t timestamp_;
	std::uint64_t orderNo_;
	char verb_;
	std::uint32_t quantity_;
	std::uint32_t orderbook_;
	char board_[LEN_BOARD];
	std::uint32_t price_;
	char reserved_[4];
	char orderType_;
};

struct TIME_TAG {
	char type_;
	uint32_t seconds_;
	void ntoh();
};

union Messages {
	ADD_TAG add_;
	REPLACE_TAG replace_;
	CANCEL_TAG cancel_;
	EXECUTE_TAG execute_;
	QUOTE_TAG quote_;
	TIME_TAG timestamp_;
};
#pragma pack(pop)

void ADD_TAG::ntoh() {
	timestamp_ = ntohl(timestamp_);
	orderNo_ = ntohll(orderNo_);
	quantity_ = ntohl(quantity_);
	orderbook_= ntohl(orderbook_);
	price_ = ntohl(price_);
	return;
}

void REPLACE_TAG::ntoh() {
	timestamp_ = ntohl(timestamp_);
	origOrderNo_ = ntohll(origOrderNo_);
	orderNo_ = ntohll(orderNo_);
	quantity_ = ntohl(quantity_);
	price_ = ntohl(price_);
	return;
}

void CANCEL_TAG::ntoh() {
	timestamp_ = ntohl(timestamp_);
	orderNo_ = ntohll(orderNo_);
}

void EXECUTE_TAG::ntoh() {
	timestamp_ = ntohl(timestamp_);
	orderNo_ = ntohll(orderNo_);
	quantity_ = ntohl(quantity_);
	matchNo_ = ntohll(matchNo_);
	return;
}

void TIME_TAG::ntoh() {
	seconds_ = ntohl(seconds_);
}

size_t getSize(char type) {
	switch (type) {
		case 'T':
			return sizeof(TIME_TAG);
		case 'S':
			return 10;
		case 'L':
			return 17;
		case 'R':
			return 45;
		case 'H':
			return 14;
		case 'A':
			return sizeof(ADD_TAG);
		case 'F':
			return sizeof(QUOTE_TAG);
		case 'E':
			return sizeof(EXECUTE_TAG);
		case 'D':
			return sizeof(CANCEL_TAG);
		case 'U':
			return sizeof(REPLACE_TAG);
		default:
			break;
	}
	std::cerr << "Unknown ITCH Message Type: " << type  << std::endl;
	exit(1);
}



class OrderBook {
public:
	OrderBook(char const * boardId, int securityId, unsigned int seconds, unsigned int nanos) : board_(boardId, LEN_BOARD), orderbook_(securityId), stoppingTime_(seconds), stoppingNanos_(nanos), lastSeenSeconds_(0), lastSeenNanos_(0) {} ;
	void printBook();
	void orderAction(struct ADD_TAG * add, bool isQuote=false);
	void orderAction(struct REPLACE_TAG * replace);
	void orderAction(struct CANCEL_TAG * cancel);
	void orderaction(struct QUOTE_TAG * quote);
	void orderAction(struct EXECUTE_TAG * execute);
	bool checkStoppingCondition(struct TIME_TAG * seconds);
private:
	std::string board_;
	unsigned int orderbook_;
	unsigned int stoppingTime_;
	unsigned int stoppingNanos_;
	unsigned int lastSeenSeconds_;
	unsigned int lastSeenNanos_;
	struct ORDER_TAG {
		long int orderNo_;
		char verb_;
		unsigned int price_;
		unsigned int quantity_;
		bool isQuote_;
	};
	typedef std::list<ORDER_TAG *> PriorityList_t;
	typedef std::map<std::uint64_t, PriorityList_t::iterator > OrderHash_t;
	typedef std::map<std::int32_t, PriorityList_t> PriceLevels_t;

	OrderHash_t orderHash_;
	PriceLevels_t priceLevels_;
};

void OrderBook::printBook() {
	PriceLevels_t::iterator l_it;
	PriorityList_t::iterator p_it;
	PriorityList_t buy_list;
	PriorityList_t sell_list;
	std::cout << "\tVerb\tOrderNo\t\t\tPrice\tQuantity\tType (Q for quote blank otherwise)" << std::endl;

	for(l_it = priceLevels_.begin(); l_it != priceLevels_.end(); l_it++) {
		for (p_it = l_it->second.begin(); p_it != l_it->second.end(); p_it++) {
			ORDER_TAG * o = *p_it;
			if (o->verb_ == 'B')
				buy_list.push_back(o);
			else
				sell_list.push_back(o);
		}
	}

	while (!sell_list.empty()) {
		ORDER_TAG * o = sell_list.back();
		sell_list.pop_back();
		std::cout << "\t" << o->verb_ << "\t" << o->orderNo_ << "\t" << o->price_ << "\t" << o->quantity_ << "\t";
		std::cout << (o->isQuote_ ? 'Q' : ' ') << std::endl;
	}

	std::cout << "\t------------------------------------------------------------------------------------------" << std::endl;

	while (!buy_list.empty()) {
		ORDER_TAG * o = buy_list.front();
		buy_list.pop_front();
		std::cout << "\t" << o->verb_ << "\t" << o->orderNo_ << "\t" << o->price_ << "\t" << o->quantity_ << "\t";
		std::cout << (o->isQuote_ ? 'Q' : ' ') << std::endl;
	}

	return;
}

void OrderBook::orderAction(struct ADD_TAG * add, bool isQuote) {
	if (add->orderNo_ == 0 || add->orderbook_ != orderbook_ || !std::strncmp(board_.c_str(), add->board_, LEN_BOARD))
		return;
	ORDER_TAG * o = new ORDER_TAG();
	o->verb_ = add->verb_;
	o->price_ = add->price_;
	o->quantity_ = add->quantity_;
	o->orderNo_ = add->orderNo_;
	o->isQuote_ = isQuote;

	PriceLevels_t::iterator p_it;
	p_it = priceLevels_.find(o->price_);
	if (p_it == priceLevels_.end()) {
		PriorityList_t l;
		priceLevels_[o->price_] = l;
	}
	priceLevels_[o->price_].push_back(o);
	PriorityList_t::iterator i = priceLevels_[o->price_].end();
	i--;
	orderHash_[add->orderNo_] = i;
	return;
}

void OrderBook::orderAction(struct REPLACE_TAG * replace) {
	OrderHash_t::iterator it = orderHash_.find(replace->origOrderNo_);
	if (it == orderHash_.end())
		return;
	ORDER_TAG * o = *it->second;

	// amend down case - priority did not change
	if (replace->origOrderNo_ == replace->orderNo_) {
		assert(o->price_ == replace->price_);
		o->quantity_ = replace->quantity_;
		return;
	}
	// delete and add again
	ADD_TAG a;
	CANCEL_TAG c;
	c.orderNo_ = replace->origOrderNo_;
	a.orderNo_ = replace->orderNo_;
	a.verb_ = o->verb_;
	a.price_ = replace->price_;
	a.quantity_ = replace->quantity_;
	bool is_quote = o->isQuote_;
	o = NULL;

	orderAction(&c);
	orderAction(&a, is_quote);

	return;
}

void OrderBook::orderAction(struct CANCEL_TAG * cancel) {
	OrderHash_t::iterator it = orderHash_.find(cancel->orderNo_);
	if (it == orderHash_.end())
		return;
	ORDER_TAG * o = *it->second;
	PriorityList_t & l = priceLevels_[o->price_];
	l.erase(it->second);
	if (l.empty())
		priceLevels_.erase(o->price_);
	orderHash_.erase(cancel->orderNo_);
	delete o;
	return;
}

void OrderBook::orderAction(struct EXECUTE_TAG * execute) {
	OrderHash_t::iterator it = orderHash_.find(execute->orderNo_);
	if (it == orderHash_.end())
		return;
	ORDER_TAG * o = *it->second;
	o->quantity_ -= execute->quantity_;
	if (o->quantity_)
		return;
	o = NULL;
	CANCEL_TAG c;
	c.orderNo_ = execute->orderNo_;
	orderAction(&c);
	return;
}

bool OrderBook::checkStoppingCondition(struct TIME_TAG * seconds) {
	if (seconds->type_ == 'T') {
		lastSeenSeconds_ = seconds->seconds_;
		lastSeenNanos_ = 0;
	}
	else
		lastSeenNanos_ = seconds->seconds_;

	if (lastSeenSeconds_ > stoppingTime_)
		return true;
	if (lastSeenSeconds_ == stoppingTime_ && lastSeenNanos_ > stoppingNanos_)
		return true;
	return false;
}

using namespace std;

int main(int argc, char ** argv) {
	char const * logfile_name;
	char board_id[LEN_BOARD];
	uint32_t orderbook_id;
	uint32_t stopping_time;
	uint32_t stopping_nano = -1;

	if (argc < 5) {
		cerr << "Usage: " << argv[0] << " <ITCHLog> <Board> <OrderbookId> <Stopping Time> <NanoSecs (OPTIONAL)>" << endl;
		return 1;
	}
	if (argc == 6)
		stopping_nano = atoi(argv[5]);

	logfile_name = argv[1];
	memset(board_id, ' ', LEN_BOARD);
	strncpy(board_id, argv[2], LEN_BOARD);
	orderbook_id = atoi(argv[3]);
	stopping_time = atoi(argv[4]);

	ifstream logfile(logfile_name, ios_base::in | ios_base::binary);
	if (!logfile.good()) {
		cerr << "IO problem with logfile: " << logfile_name << endl;
	}
	OrderBook order_book(board_id, orderbook_id, stopping_time, stopping_nano);
	char type;
	int sequence_number = 0;
	while (!logfile.eof()) {
		sequence_number++;
		uint16_t message_length;
		size_t expected_length;
		message_length = expected_length = 0;
		logfile.read((char *)&message_length, 2);
		message_length = ntohs(message_length);
		type = logfile.peek();
		if (logfile.eof())
			break;

		expected_length = getSize(type);
		if (message_length != expected_length) {
			cerr << "Message decode failed. Logfile reports size of " << message_length;
			cerr << " but expected: " << expected_length << endl;
			exit(1);
		}
		Messages message;

		if (message_length > sizeof(message)) {
			logfile.ignore(message_length);
			continue;
		}
		logfile.read((char *)&message, message_length);
		if (logfile.eof())
			break;

		/* All ITCH mesages have Type and 32bit field to indicate time
		 * If the type is T then the following field is seconds since midngiht.
		 * Otherwise, it is nanoseconds since the T message was reported
		 */
		TIME_TAG current_time = message.timestamp_;
		current_time.ntoh();
		if (order_book.checkStoppingCondition(&current_time))
			break;

		switch (type) {
			case 'A':
				message.add_.ntoh();
				order_book.orderAction(&message.add_);
				break;
			case 'U':
				message.replace_.ntoh();
				order_book.orderAction(&message.replace_);
				break;
			case 'D':
				message.cancel_.ntoh();
				order_book.orderAction(&message.cancel_);
				break;
			/* We can treat the F message as an add message since it follows the same layout.
			 * Just double check the orderType is 'Q'
			 */
			case 'F':
				message.add_.ntoh();
				if (message.quote_.orderType_ == 'Q')
					order_book.orderAction(&message.add_, true);
				else
					order_book.orderAction(&message.add_, false);
				break;
			case 'E':
				message.execute_.ntoh();
				order_book.orderAction(&message.execute_);
				break;
			default:
				break;
		}
	}
	logfile.close();
	order_book.printBook();
	return 0;
}

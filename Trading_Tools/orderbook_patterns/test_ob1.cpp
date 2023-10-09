/* g++ -o test_ob{,.cpp}
*
*  Note:
*  - Accumulating order book : Adds qty at a price level
*  - Uses double in bid ask map key => Should be avoided
*
*/
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <algorithm>
#include <map>
#include <cmath>

typedef std::map<double,int > omap;
typedef std::pair<double,int> opair;


enum Side
{
    Side_BID,
    Side_ASK
};

inline const char* toString(Side side)
{
    return side == Side_BID ? "Bid" : "Ask";
}

enum SecurityStatus
{
    Status_ACTIVE,
    Status_SUSPENDED
};



class OrderBook {
public:
    OrderBook() : m_boardid(""), m_status(Status_ACTIVE) { }
    OrderBook(std::string board, SecurityStatus status) :  m_boardid(board),
                                                           m_status(status) { }
    void insert_order(Side o_side, double prc, int qty);
    void delete_order(Side o_side, double prc, int qty);
    void execute(int buy_ono, double prc, int qty);
    bool set_status(SecurityStatus status);
    void print_book(const OrderBook &);
    void print_msg_details(const char* str, Side o_side, double prc, int qty);

    //int m_order_no;
    std::string m_boardid;
    SecurityStatus m_status;
    omap m_bid_map;
    omap m_ask_map;
};


void OrderBook::insert_order(Side o_side, double prc, int qty){
    OrderBook::print_msg_details("ADD", o_side, prc, qty);
    //printf("\tinsert_order: prc=%.30f price=%ld\n", prc, price);
    printf("\tinsert_order: prc=%.30f\n", prc);

    if(o_side == Side_BID){

        omap::iterator itt = m_bid_map.find(prc);

        if(itt == m_bid_map.end())
            m_bid_map.insert(opair(prc, qty)); //XXX Add Insert Failed condn
        else{
            itt->second = itt->second + qty;
        }

    }else{
        omap::iterator itt = m_ask_map.find(prc);

        if(itt == m_ask_map.end())
            m_ask_map.insert(opair(prc, qty)) ;// Add Insert failed condn
        else{
            itt->second = itt->second + qty;
        }
    }
}

void execute(int sell_ono, int buy_ono, double prc, int qty){
/*
    OrderBook::print_msg_details("EXEC", order_no, NULL, prc, qty);

    if(o_side == Side_BID){
        omap::iterator itt = m_bid_map.find(prc);

        if(itt != m_bid_map.end()){
            itt->second = qty;
        }else{
            std::cout << std::endl << "Bid Update failed" << std::endl;
        }

    }else{
        omap::iterator itt = m_ask_map.find(prc);

        if(itt != m_ask_map.end()){
            itt->second = qty;
        }else{
            std::cout << std::endl << "Ask Update failed" << std::endl;
        }
    }
*/
}

void OrderBook::delete_order(Side o_side, double prc, int qty){
    print_msg_details("DEL", o_side, prc, qty);

    if(o_side == Side_BID){
        omap::iterator itt = m_bid_map.find(prc);

        if(itt != m_bid_map.end()){

            if(itt->second <= qty){
                m_bid_map.erase (itt);
            }else{
                itt->second = itt->second - qty;
            }

        }else{
            std::cout << "Remove failed" << std::endl;
        }

    }else{
        omap::iterator itt = m_ask_map.find(prc);

        if(itt != m_ask_map.end()){

            if(itt->second <= qty){
                m_ask_map.erase (itt);
            }else{
                itt->second = itt->second - qty;
            }

        }else{
            std::cout << std::endl << "Remove failed" << std::endl;
        }
    }
}

bool OrderBook::set_status(SecurityStatus status){
    if(status == Status_ACTIVE || status == Status_SUSPENDED){
        m_status = status;
        return true;
    }else
        return false;
}
void OrderBook::print_book(const OrderBook &ob){

    std::cout << std::endl;
    std::cout << "----BID Map------" << std::endl;
    std::cout.setf(std::ios::fixed);
    for( omap::const_iterator i= ob.m_bid_map.begin(); i!=ob.m_bid_map.end(); ++i){
        std::cout << std::setprecision(2) << (*i).first << ": " << (*i).second << std::endl;
    }

    std::cout << std::endl;
    std::cout << "----ASK Map------" << std::endl;
    for( omap::const_iterator i= ob.m_ask_map.begin(); i!= ob.m_ask_map.end(); ++i){
        std::cout << (*i).first << ": " << (*i).second << std::endl;
    }
}

void OrderBook::print_msg_details(const char* str, Side o_side, double prc, int qty){
    if(o_side == Side_BID || o_side == Side_ASK){
        printf("\nMsg: %s Side : %s\t", str, toString(o_side));
        std::cout.setf(std::ios::fixed);
        std::cout << "Price :" << std::setprecision(2) << prc << " Qty :" << qty;
    }
}


int main ()
{

    std::map<int,OrderBook> orderbooks;

    orderbooks[1301] = OrderBook("DAY", Status_ACTIVE);
    orderbooks[1305] = OrderBook("DAY", Status_ACTIVE);
    orderbooks[1306] = OrderBook("DAY", Status_ACTIVE);


    //OrderBook ob("DAY", Status_ACTIVE);
    OrderBook ob = orderbooks[1306];


/*
    double j = 100;
    for (int i=0; i< 5; ++i,j+=0.1){
        ob.insert_order(1301,Side_BID,j,1000);
        ob.insert_order(1301,Side_BID,j,1000);
    }

    for (int i=0; i< 5; ++i,j+=0.1){
        ob.insert_order(1301,Side_ASK,j,1000);
        ob.insert_order(1301,Side_ASK,j,1000);
    }
*/

    //Insert
    ob.insert_order(Side_BID,100.00,1000);
    ob.insert_order(Side_BID,100.0,1000);
    ob.insert_order(Side_BID,100.10,1000);
    ob.insert_order(Side_BID,100.20,1000);
    ob.insert_order(Side_BID,100.30,1000);
    ob.insert_order(Side_BID,100.40,1000);
    ob.insert_order(Side_BID,100.50,1000);

    ob.insert_order(Side_ASK,100.60,1000);
    ob.insert_order(Side_ASK,100.70,1000);
    ob.insert_order(Side_ASK,100.80,1000);
    ob.insert_order(Side_ASK,100.90,1000);
    ob.insert_order(Side_ASK,100.90,1000);
    ob.insert_order(Side_ASK,101.10,1000);

    ob.print_book(ob);
    ob.delete_order(Side_BID,100,1000);
    ob.delete_order(Side_BID,100.1,1000);
    ob.delete_order(Side_ASK,100.60,1000);

    ob.print_book(ob);
    //ob.insert_order(Side_ASK,100.90,1000);

    //Update Functionality
    ob.delete_order(Side_ASK,100.90,2000);
    ob.insert_order(Side_ASK,100.50,3000);

    ob.print_book(ob);
    return 0;
}

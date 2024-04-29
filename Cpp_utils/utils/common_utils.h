#ifndef COMMON_UTILS_H
#define COMMON_UTILS_H

#include <string>
#include <sstream>

namespace kutil{
/*


    //trim from start
    static inline std::string &ltrim(std::string &s){
        s.erase(s.begin(), std::find_if(s.begin(), s.end(), std::not1(std::ptr_fun<int, int>(std::isspace))));
        return s;
    }

    //trim from end
    static inline std::string &rtrim(std::string &s){
        s.erase(std::find_if(s.rbegin(), s.rend(), std::not1(std::ptr_fun<int, int>(std::isspace))).base(), s.end());
        return s;
    }

*/

    //Trim All Spaces Inside String
    inline std::string trim(std::string& str)
    {
        str.erase(0, str.find_first_not_of(' '));       //prefixing spaces
        str.erase(str.find_last_not_of(' ')+1);         //surfixing spaces
        return str;
    }

    //Simon's Pie's
    /*
    Usage :
            int i = 42;
            double d = 3.14;
            string s1 = toString(i);
            string s2 = toString(d);
            cout << s1 << ' ' << s2 << endl;

            string s3("84");
            int j = fromString<int>(s3);
            double e = fromString<double>("6.28");
            cout << j << ' ' << e << endl;

    */

    template <typename T>
    inline std::string toString(const T& t)
    {
        std::ostringstream oss;
        oss.setf(std::ios::fixed);
        oss << t;
        return oss.str();
    }


    template <typename T>
    inline T fromString(const std::string& s)
    {
        std::istringstream iss(s);
        T t;
        iss >> t;
        return t;
    }

}; //namespace
#endif

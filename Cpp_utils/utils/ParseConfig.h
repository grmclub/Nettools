#ifndef PARSECONFIG_H
#define PARSECONFIG_H

#include <iostream>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <cstring>
#include <string>
#include<map>

#include "common_utils.h"

#define CONFIGBUFSIZE 1024
typedef std::map< std::string, std::string > config_map;

class ParseConfig
{
public:
    ParseConfig(){};
    ~ParseConfig(){};

    bool readConfigFile(const std::string&);

    std::string getCfg_str(const std::string&);
    double getCfg_dbl(const std::string&);
    int getCfg_int(const std::string&);
    long getCfg_long(const std::string&);
    void printcfg();

private:
    config_map config_val;

};

#endif //PARSECONFIG_H

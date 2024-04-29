#include "ParseConfig.h"

bool ParseConfig::readConfigFile(const std::string& filename)
{
    char line[CONFIGBUFSIZE];
    std::string f_line;
    std::string key;
    std::string value;
    int end;

    //Try to Open Config File
    std::ifstream infile(filename.c_str());
    if ( !infile ) {
        std::cerr<<"std::error:"<<"Config File Not Found"<<std::endl;
        return false;
    }

    while (!infile.eof()) {
        //read data from file
        //std::getline (infile,f_line);
        infile.getline(line,CONFIGBUFSIZE);
        f_line.assign(line);

        //Trim Whitespaces
        f_line = kutil::trim(f_line);

        size_t pos = f_line.find_first_not_of(" \t",0);

        //Eliminate Blank Lines & Comments
        if (pos != std::string::npos && f_line[pos] != '#') {

            end = f_line.find_first_of("=",0);

            //Take Care not to put values without keys
            if (end > 0) {
                key = f_line.substr(0,end);
                value = f_line.substr(end+1);

                //Put key:value pair into Class Variable
                config_val.insert(std::make_pair(key,value));
            }

        }
    }
    //Finish & Close FileHandle
    infile.close();
    return true;
}

std::string ParseConfig::getCfg_str(const std::string& key)
{
    //Process if Config is Empty return
    if ((int)config_val.size() == 0)
        return "";

    config_map::iterator itr_cfg = config_val.find(key);

    //Process if Key does not Exist
    if (itr_cfg == config_val.end())
        return "";

    return itr_cfg->second;

}

double ParseConfig::getCfg_dbl(const std::string& key)
{
    //Process if string is empty
    if (key.empty())
        return -1;

    std::string strVal = getCfg_str(key);

    //Process if Key does not Exist
    if (strVal.empty())
        return -1;

    return atof(strVal.c_str());
}

int ParseConfig::getCfg_int(const std::string& key)
{
    //Process if string is empty
    if (key.empty())
        return -1;

    std::string strVal = getCfg_str(key);

    //Process if Key does not Exist
    if (strVal.empty())
        return -1;

    return atoi(strVal.c_str());
}

long ParseConfig::getCfg_long(const std::string& key)
{
    //Process if string is empty
    if (key.empty())
        return -1;

    std::string strVal = getCfg_str(key);

    //Process if Key does not Exist
    if (strVal.empty())
        return -1;

    return atol(strVal.c_str());
}

void ParseConfig::printcfg() {

    std::cout << "Config Size : "<<config_val.size() << std::endl;

    config_map::iterator itr_cfg;
    for(itr_cfg = config_val.begin(); itr_cfg != config_val.end(); itr_cfg++) {

        std::cout << (*itr_cfg).first << " => "<<(*itr_cfg).second << std::endl;
    }
}

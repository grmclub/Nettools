#include "ParseConfig.h"

bool ParseConfig::readConfigFile(const std::string& filename)
{
    char line[CONFIGBUFSIZE];
    std::string f_line;
    std::string key;
    std::string value;
    int end;

    std::ifstream infile(filename.c_str());
    if ( !infile ) {
        std::cerr<<"std::error:"<<"Config File Not Found"<<std::endl;
        return false;
    }

    while (!infile.eof()) {
        infile.getline(line,CONFIGBUFSIZE);
        f_line.assign(line);

        //Trim whitespaces
        f_line = kutil::trim(f_line);
        size_t pos = f_line.find_first_not_of(" \t",0);

        //Eliminate blank lines & comments
        if (pos != std::string::npos && f_line[pos] != '#') {
            end = f_line.find_first_of("=",0);

            //Exclude values without keys
            if (end > 0) {
                key = f_line.substr(0,end);
                value = f_line.substr(end+1);
                config_val.insert(std::make_pair(key,value));
            }
        }
    }
    infile.close();
    return true;
}

std::string ParseConfig::getCfg_str(const std::string& key)
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
    if (key.empty())
        return -1;
    std::string strVal = getCfg_str(key);

    if (strVal.empty())
        return -1;
    return atof(strVal.c_str());
}

int ParseConfig::getCfg_int(const std::string& key)
{
    if (key.empty())
        return -1;
    std::string strVal = getCfg_str(key);
	
    if (strVal.empty())
        return -1;
    return atoi(strVal.c_str());
}

long ParseConfig::getCfg_long(const std::string& key)
{
    if (key.empty())
        return -1;
    std::string strVal = getCfg_str(key);

    if (strVal.empty())
        return -1;
    return atol(strVal.c_str());
}

void ParseConfig::printcfg()
{
    std::cout << "Config Size : "<<config_val.size() << std::endl;
    config_map::iterator itr_cfg;
    for(itr_cfg = config_val.begin(); itr_cfg != config_val.end(); itr_cfg++) {
        std::cout << (*itr_cfg).first << " => "<<(*itr_cfg).second << std::endl;
    }
}

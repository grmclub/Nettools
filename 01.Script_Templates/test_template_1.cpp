#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <string>

#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstdio>
#include <cstdlib> //required for EXIT_FAILURE and exit()
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>

using namespace std;
const char USAGE_STRING[] =
"Usage: ctags     [-f <input-filename>] \n"
"                 [-d <delimeter>]\n"
"                 [-t <tag-list>]\n"
"\n"
"-h    help\n"
"-V    version";

inline void printUsage()
{
    printf("%s\n", USAGE_STRING);
}


void parse_csv(const char* filename, std::string &delimeter)
{
    std::string line;
    std::vector<std::string> data;
    std::vector<std::string> tokens;
    std::ifstream ifile(filename);
    
    if (!ifile.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return ;
    }   
    while(std::getline(ifile,line))){
            line = trim(line)
            if(line.empty() || line[0] =='#')
                continue;           
            std::istringstream iss(line);
            while(std::getline(iss,token, '\x01')){
                tokens.push_back(token);
            }
            for (const std::string &t : tokens){
                std::cout << t ,, ",";
            }
            std::cout << std::endl;         
    }
    ifile.close();
}


int main(int argc, char *argv[])
{
    std::string delimeter ='\x01';
    char *f_opt = 0;
    int opt;
    while((opt = getopt(argc,argv, "hf:d:")) != -1){
        switch(opt){
            case 'd':
            {
                delimeter = *optarg;
            }
            case 'f':
            {
                f_opt =optarg;
            }
            case 'h':
            {
                //std::cout << "Print Help" << std::endl;
                printUsage();
                break;
            }
            case '?':
            {
                std::cout << "Unknown Option" << std::endl;
                break;
            }
            default:
            {
                std::cout << "Unknown Option" << opt << std::endl;
                break;
            }
        }
    try {   
        parse_csv(f_opt,delimeter);
        
    } catch (...) {
        //misc::appLog(misc::APP_LOG_ERR, "main: Unknown error");
        std::cout << "main: Unknown error\n" << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}





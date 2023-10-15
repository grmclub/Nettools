#!/usr/bin/env python

import os, sys, getopt
import errno, traceback
import csv
import subprocess

def printHelp():
    print ("""Usage: %s -f <filename>

    OPTIONS:
         -f  host list file
         -l  select scrape list (HW,CPU,MEM,DISK,NET,OS,GCC,JAVA)
         -h  Display this help message.
    """ % os.path.basename(__file__))

def execCmd(cmd):
    #print (cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.returncode
    return (output,err,ret)


class estate_scraper:
    def __init__(self):
        self.host_list = []
        self.scrape_list = {}
        self.scrape_select = "HW,CPU,MEM,OS,NET,JAVA"
        self.scrape_list["HW"]  ="cat /sys/devices/virtual/dmi/id/product_name"
        self.scrape_list["CPU"] ="lscpu|egrep 'Arch|Core|Socket|Model'|paste -d';' - - - -|tr -s ' '"
        self.scrape_list["MEM"] ="free -h|grep Mem|awk '{print \$1,\$2}'"
        self.scrape_list["DISK"] ="lsblk -d -o NAME,SERIAL,SIZE"
        self.scrape_list["NET"] ="lspci|grep Ethernet"
        self.scrape_list["OS"]  ="lsb_release -d";
        self.scrape_list["GCC"] ="gcc --version|grep -i gcc"
        self.scrape_list["JAVA"]="env|grep -i java_home"

    def process_host_file(self,host_file):
        with open(host_file, "r") as ifile:
            for line in ifile:
                line = line.strip()
                if line  and not line.startswith("#"):
                    #print line
                    self.host_list.append(line)

    def process_host_list(self,host_list):
        self.host_list = host_list.split(",")
    def process_scrape_select(self,scrape_select):
        self.scrape_select = scrape_select

    def run_scrape(self):
        cmd = ""
        for key in self.scrape_select.split(","):
            #print key
            cmd = cmd + self.scrape_list[key] + ";"

        for host in self.host_list:
            print("host:%s" %host)
            cmd2 = "ssh %s \"%s\" </dev/null" % (host, cmd)
            #print(cmd2)
            result,e,r = execCmd(cmd2)
            print(result)
            print("=====")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:l:H:h")
    except getopt.GetoptError as e:
        print (e)
        sys.exit()

    try:
        HOST_FILE  = ""
        SCRAPE_LIST = ""
        HOST_LIST  = ""
        for o,a in opts:
            if o == "-f":
                HOST_FILE = a
            if o == "-l":
                SCRAPE_LIST = a
            if o == "-H":
                HOST_LIST = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        est_scraper = estate_scraper()
        if (SCRAPE_LIST):
            est_scraper.process_scrape_select(SCRAPE_LIST)
        if (HOST_FILE):
            est_scraper.process_host_file(HOST_FILE)
        if (HOST_LIST):
            est_scraper.process_host_list(HOST_LIST)

        est_scraper.run_scrape()

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()


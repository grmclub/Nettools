#!/usr/bin/env python3

import os, sys, getopt
import errno, traceback
import csv
import subprocess


def printHelp():
    print ("""Usage: %s -f <filename>
    
    ##header
    11111,35,39,54,49,56,58

    OPTIONS:
         -f  host list file
         -h  Display this help message.
    """ % os.path.basename(__file__))

def process_file(data_file,delm):
    id_dict     = {}

	for line in in datafile:
		row = line.strip().split(delm)
		msgtype    = row[0].replace('"','')
		execype    = row[1]
		side       = row[2]
		sender     = row[3]
		target     = row[4]
		text       = row[5]

		if msgtype == "D":
			if id_dict.get(sender):
				id_dict[sender]["new"] += 1
			else:
				id_dict[sender]={"new":1, "buy": 0, "sell":0, "ss":0, "ioc_rej":0}
				
			if side  == "1":
				id_dict[sender]["buy"] += 1
			if side  == "2":
				id_dict[sender]["sell"] += 1
			if side  == "5":
				id_dict[sender]["ss"] += 1
			
		if msgtype == "8" and side == "5" and "UNABLE TO ACCEPT FULL QTY" in test:
			id_dict[target]["ioc_rej"] += 1

	for key in sorted(id_dict.keys()):
		x = id_dict[key]
		print("%s,%s,%s,%s,%s" % (x["buy"],x["sell"],x["ss"],x["ioc_rej"]))                                                 
  
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h")
    except getopt.GetoptError as e:
        print (e)
        sys.exit()

    try:
        DATA_FILE = ""
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        if (DATA_FILE):
            process_file(DATA_FILE)

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()

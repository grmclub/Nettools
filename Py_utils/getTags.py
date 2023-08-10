#!/usr/bin/env python

import os, sys, getopt
import errno, traceback

def printHelp():
    print """Usage: %s -f <filename>

    OPTIONS:
         -d delimeter
		 -l extract log timestamp
		 -t tag list (tag1,tag2)
         -h Display this help message.
    """ % os.path.basename(__file__)
	sys.exit(0)

def format_str(str):
	result = str[:-1] if str[-1] == "," else str
	return result

def process_file(data_file,delm_tag,tag_list,log_ts_flag):
	print tag_list
	tag_list = tag_list.split(",")
	tl_size = len(tag_list)
	row_dict= {}
	log_ts = ""
	for line in data_file:
		line = line.strip().split(delm)
		row_dict.clear()
		for item in line:
			item = item.split('=')
			if len(item) == 2:
				if item[0] in tag_list:
					row_dict[item[0]] = item[1]

		str = ""
		for key in tag_list:
			if row_dict.get(key) is None:
				row_dict[key] = ""
			str = str + row_dict[key] + ","

		if log_ts_flag:
			log_ts =line[0][0:15]
			if log_ts[0:2].isdigit():
				print("%s,%s" % (log_ts,format_str(str)))
		else:
			print format_str(str)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:f:lt")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        DATA_FILE = sys.stdin
		DELM = "\001"
		TAG_LIST= ""
		LOG_TS_FLAG = False

        for o,a in opts:
            if o == "-d":
                DELM = a
            if o == "-l":
                LOG_TS_FLAG = True
            if o == "-t":
                TAG_LIST = a
			if o == "-f":
                DATA_FILE = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        process_file(DATA_FILE,DELM,TAG_LIST,LOG_TS_FLAG)

    except Exception, err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()

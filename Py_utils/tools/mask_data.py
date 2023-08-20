#!/usr/bin/env python

#import os, sys, getopt
import os, sys, getopt
import errno, traceback
import subprocess
import datetime
import csv
import base64

def printHelp():
    print """Usage: %s -i <input_file> -o <output_file> -m <mask_fields>

    OPTIONS:
         -i  input file
		 -o  otput file
		 -m  mask fields
         -h  Display this help message.
    """ % os.path.basename(__file__)  # sys.argv[0]

def encode(str):
	str = base64.b64.encode(str)
	return str
	
def process_row(row):
	str = (",".join(row))
	return str.replace("[NULL]", "")

		
def process_file(in_file,out_file,mask_fields):
	mask_set = set()
	for field in mask_fields.split(","):
		mask_set.add(int(field))
		
	with open(in_file, "r") as ifile:
		reader = csv.reader(ifile)
		
		header =""
		nrow =0
		ncol=0
		for row in reader:
			if nrow == 0:
				nrow = 1
				header = row
				print (process_row(header))
				ncol= len(next(reader))
			else:
				for col in range(0,col):
					if col in mask_set:
						row[col] = encode(row[col])
				print(process_row(row))
						

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:m:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        IN_FILE = ""
		OUT_FILE = ""
		FIELD_LIST = ""
        for o,a in opts:
            if o == "-i":
                IN_FILE = a
            if o == "-o":
                OUT_FILE = a
            if o == "-m":
                FIELD_LIST = a				
            if o == "-h":
                printHelp()
                sys.exit(0)

        process_file(IN_FILE,OUT_FILE,FIELD_LIST)

    except Exception, err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()
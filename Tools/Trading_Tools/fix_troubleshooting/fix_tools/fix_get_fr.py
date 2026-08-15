#!/usr/bin/env python3

import os, sys, getopt
import errno, traceback
import csv

def printHelp():
    print ("""Usage: %s -f <filename>

    OPTIONS:
         -f  host list file
         -h  Display this help message.
         
         #12100,376,150,38,32
         cat fix_log| egrep -a “150=[012]”| gtags -t 1,376,150,38,32 > all_fix
         
    """ % os.path.basename(__file__))

def process_file(data_file):
	acct_dict = {}
	with open(data_file, "r") as ifile:
		reader = csv.reader(ifile)
		for row  in reader:
			rtpc_acct = row[0]
			comp_id   = row[1]
			exec_type = row[2]
			qty       = row[3]
			fill_qty  = row[4]
			#print("%s,%s,%s,%s,%s" % (rtpc_acct,comp_id,exec_type,qty,fill_qty))

			if not acct.dict.get(rtpc _acct):
				acct_dict[rtpc_acct] = {'total_qty':0, 'total_fill_qty':0, 'ord_cnt':0, 'fill_cnt':0 }

			if exec_type == "0":
				acct_dict[rtpc_acct]['total_qty'] += int(qty)
				acct_dict[rtpc_acct]['order_cnt'] += 1

			if exec_type == 1 or 2:
				acct_dict[rtpc_acct]['total_fill_qty'] += int(qty)
				acct_dict[rtpc_acct]['fill_cnt'] += 1

    print('acct,ord_cnt,total_qty,fill_cnt,fill_qty,fill_ratio')
    for acct in sorted(acct_dict.keys()):
        x = acct_dict[acct]
        fill_ratio = (x['total_fill_qty']/(float) x['total_qty'])*100
        print("%s,%d,%d,%d,%d,%0.2f"%(acct,x['ord_cnt'],x['total_qty'], x['fill_cnt'], x['total_fill_qty'], fill_ratio))


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h")
    except getopt.GetoptError as e:
        print (e)
        sys.exit()

    try:
        DATA_FILE = sys.stdin
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
        print("Error: %s\n" % str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()
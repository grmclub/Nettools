#!/usr/bin/env python3

import os, sys, getopt
import errno, traceback
import csv
from collections import OrderedDict


def printHelp():
    print ("""Usage: %s -f <filename>

    ##header
    11111,35,39,11,41,49,56,9245,52,54,59,12124,38,44,376,151,14

    OPTIONS:
         -f  host list file
         -h  Display this help message.
    """ % os.path.basename(__file__))

def process_file(data_file):
    id_dict = OrderedDict()
    client_dict = {}

    with open(data_file, "r") as ifile:
        reader = csv.reader(ifile)
        for row in reader:
            t11111 = row[0]
            t35    = row[1]
            t39    = row[2]
            t11    = row[3]
            t41    = row[4]
            t49    = row[5]
            t56    = row[6]
            t9245  = row[7]
            t52    = row[8]
            t54    = row[9]
            t59    = row[10]
            t12124 = row[11]
            t38    = row[12]
            t44    = row[13]
            t376   = str(row[14])
            t151   = row[15]
            t14    = row[16]

            #print(t11111,t35,t39,t11,t41,t49,t56,t9245,t52,t54,t59,t12124,t38,t44,t376,t151,t14)
            if t35 == "D":
                id_dict[t376] = {
                                    "11111"      : t11111,
                                    "sess"       : t49,
                                    "cl_acr"     : t9245,
                                    "clordid"    : t11,
                                    "oclordid"   : t41,
                                    "tif"        : t59,
                                    "side"       : t54,
                                    "ord_status" : t39,
                                    "ord_time"   : t52,
                                    "ord_qty"    : t38,
                                    "sym"        : t12124,
                                    "cxl_time"   : "",
                                    "cxl_qty"    : 0
                                }
                #print(id_dict[t376])
            elif t35 == "F":
                if id_dict.get(376):
                    id_dict[t376]["cxl_time"] = t52
                    id_dict[t376]["oclordid"] = t41
                    id_dict[t376]["ord_status"] = t39
            elif t35 == "8":
                if id_dict.get(376):
                    id_dict[t376]["ord_status"] = t39

    print("11111,Session,Acronym,11,41,Tif,Side,Ord_Time,Symbol,Ord_Qty,Cxl_Time,Cxl_Qty,Comp_id")
    for key in id_dict.keys():
        x = id_dict[key]
        if (x["ord_status"] == "A"):
            print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ( x['11111'],
                                                               x["sess"],
                                                               x["cl_acr"],
                                                               x["clordid"],
                                                               x["oclordid"],
                                                               x["tif"],
                                                               x["side"],
                                                               x["ord_time"],
                                                               x["sym"],
                                                               x["ord_qty"],
                                                               x["cxl_time"],
                                                               x["cxl_qty"],
                                                               key))

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

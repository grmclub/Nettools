#!/usr/bin/env python3

import os, sys, getopt
import errno, traceback
import csv
from decimal import Decimal
import subprocess


def printHelp():
    print ("""Usage: %s -f <filename>
    
    ##header
    11111,35,39,11,41,49,56,9245,52,54,59,12124,38,44,376,151,14,31,32,1

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
            t376   = row[14]
            t151   = row[15]
            t14    = row[16]
            t31    = row[17]
            t32    = row[18]
            t1     = row[19]
            
            #print(t11111,t35,t39,t11,t41,t49,t56,t9245,t52,t54,t59,t12124,t38,t44,t376,t151,t14,t31,t32,t1)
            if t35 == "D":
                client_key = t9245 + "," + t1 + "," + t59
                
            if client_dict.get(client_key):
                client_dict[client_key]["ord_count"] += 1
                client_dict[client_key]["ord_vol"  ] += int(t38)
                client_dict[client_key]["ord_value"] += float("%0.2f" %(int(t38)*float(t44)))
                
            else:
                client_dict[client_key] = { "ord_count":1,
                                            "ord_vol"  : int(t38),
                                            "ord_value": float("%0.2f" %(int(t38)*float(t44))),
                                            "ioc_count":0,
                                            "fill_count":0,
                                            "fill_vol":0,
                                            "fill_value":0,
                                            "cxl_count":0,
                                            "cxl_vol":0,
                                            "cxl_value":0,
                                            "rej_count":0,
                                            "rej_vol":0,
                                            "rej_value":0
                                          }
            if t59 == "3":
                client_dict[client_key]["ioc_count"] += 1
                id_dict[t376] = { 
                                "11111"      = t11111,
                                "clordid"    = t11,
                                "oclordid"   = t41,
                                "sess"       = t49,
                                "cl_acr"     = t9245,
                                "ord_time"   = t52,
                                "side"       = t54,
                                "tif"        = t59,
                                "sym"        = t12124,
                                "ord_qty"    = t38,
                                "ord_price"  = t44,
                                "cl_account" = t1                     
                            }

            elif t35 == "8":
                if id_dict.get(t376):
                    x = id_dict[t376]
                    client_key = x["cl_acr"] + "," + x["cl_account"] + "," + x["tif"]
                    if client_dict.get(client_key):
                        if (t39 == "1" or t39 == "2"):
                            client_dict[client_key]["fill_count"] += 1
                            client_dict[client_key]["fill_vol"  ] += int(t32)
                            client_dict[client_key]["fill_value"] += float("%0.2f" %(int(t32)*float(t31)))
                        elif (t39 == "4"):
                            client_dict[client_key]["cxl_count"] += 1
                            client_dict[client_key]["cxl_vol"  ] += int(t32)
                            client_dict[client_key]["cxl_value"] += float("%0.2f" %(int(t32)*float(t31)))
                        elif (t39 == "8"):
                            client_dict[client_key]["rej_count"] += 1
                            client_dict[client_key]["rej_vol"  ] += int(t32)
                            client_dict[client_key]["rej_value"] += float("%0.2f" %(int(t32)*float(t31))) 

    print("acronym,tag1,ioc,ord_count,ord_vol,ord_value,fill_count,fill_vol,fill_value,cxl_count,cxl_vol,cxl_value,rej_count,rej_vol,rej_value")
    for key in sorted(client_dict.keys()):
        x = client_dict[key]
        print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %( key,
                                                          x["ord_count"],
                                                          x["ord_vol"  ],
                                                          ("%0.2f" % x["ord_value"]),
                                                          x["fill_count"],
                                                          x["fill_vol"  ],
                                                          ("%0.2f" % x["fill_value"]),
                                                          x["cxl_count"],
                                                          x["cxl_vol"  ],
                                                          ("%0.2f" % x["cxl_value"]),
                                                          x["rej_count"],
                                                          x["rej_vol"  ],
                                                          ("%0.2f" % x["rej_value"])))                                                       
  
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

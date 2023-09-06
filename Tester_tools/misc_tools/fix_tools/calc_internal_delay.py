#!/usr/bin/env python3

import os, sys, getopt
import errno,traceback
import subprocess
import datetime
import csv


def printHelp():
    print ("""Usage: %s -f <filename>

    OPTIONS:
         -f  input file
         -l compare log_ts and transact_ts
         -h  Display this help message.

    Extract tags : 52,60,11
    #./calc_fix_delay.py -f <extracted file> |sort -t',' -nrk4 | head -15

    """ % os.path.basename(__file__))


# WIP : Calc process _delay & log_delay in one function
#

def process_tags(data_file):
    with open(data_file, "r") as ifile:
        reader = csv.reader(ifile)
        today  = datetime.date.today().strftime("%Y%m%d")
        offset = datetime.datetime.now() - datetime.datetime.utcnow()

        for row in reader:
            # exclude header row.
            if row[0] == "52":
                continue
            else:
                sending_t  = row[0]
                transact_t = row[1]
                clordid    = row[2]

                if sending_t != '' and transact_t != '':
                    st = datetime.datetime.strptime(sending_t, "%Y%m%d-%H:%M:%S.%f").strftime("%s.%f")
                    tt = datetime.datetime.strptime(transact_t, "%Y%m%d-%H:%M:%S.%f").strftime("%s.%f")
                    delay = abs(float(tt) - float(st))
                    if transact_t !=0:
                        print("%s,%s,%s,%f" % (sending_t,transact_t,clordid,delay))

def process_logtime(data_file):
    with open(data_file, "r") as ifile:
        reader = csv.reader(ifile)
        today  = datetime.date.today().strftime("%Y%m%d")
        offset = datetime.datetime.now() - datetime.datetime.utcnow()

        for row in reader:
            log_t = row[0].split("-")[1]
            lt = today + '-' + log_t.strip()
            lt_calc = datetime.datetime.strptime(lt, "%Y%m%d-%H:%M:%S.%f")
            lt_calc = lt_calc - offset
            lt_calc = lt_calc.strftime("%s.%f")

            #sending_t  = row[0]
            transact_t = row[1]
            transact_t = transact_t[0:24]
            clordid    = row[2]

            if "-" in transact_time:
                #st = datetime.datetime.strptime(sending_t, "%Y%m%d-%H:%M:%S.%f").strftime("%s.%f")
                tt = datetime.datetime.strptime(transact_t, "%Y%m%d-%H:%M:%S.%f").strftime("%s.%f")
            else:
                transact_t = 0
                tt = str(0)

            delay = abs(float(lt_calc) - float(tt))
            if transact_t !=0:
                #print("%s,%s,%s,%f" % (sending_t,ransact_t,clordid,delay))
                print("%s,%s,%s,%f" % (lt,ransact_t,clordid,delay))

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:lh")
    except getopt.GetoptError as e:
        print(e)
        sys.exit()

    try:
        DATA_FILE = ""
        LOG_FLAG = False
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-l":
                LOG_FLAG = True
            if o == "-h":
                printHelp()
                sys.exit(0)

        if LOG_FLAG:
            process_logtime(DATA_FILE)
        else:
            process_tags(DATA_FILE)

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()



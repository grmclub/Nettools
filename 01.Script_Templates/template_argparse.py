#!/usr/bin/env python

import os
import sys
import argparse
import datetime
import traceback

def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%d")

def main():
    try:
        arg_date_chk = False
        arg_list     = ""
        parser = argparse.ArgumentParser(prog='main',
                                         description='Generate report for clients')

        parser.add_argument('-p', '--bypass',
                            help=' by-pass business date check',
                            action='store_true',
                            required=False)

        parser.add_argument('-d', '--valuation_date',
                            help='valuation date in YYYY-MM-DD',
                            required=True)

        parser.add_argument('-j', '--input_csv',
                            help='input csv file provided by XX',
                            required=True)


        parser.add_argument('-m', '--member',
                            help='Member List',
                            required=False)

        parser.add_argument('-x', '--vendor',
                            help='Vendor List',
                            required=False)

        parser.add_argument('-X', '--common',
                            help='Output to Common',
                            action='store_true',        #XXX validate
                            required=False)

        parser.add_argument('-n', '--exclude_mbr',
                            help='Exclude Member',
                            required=False)

        parser.add_argument('-v', '--exclude_vendor',
                            help='Exclude Vendor',
                            required=False)


        #parser.add_argument('-h', '--help',
        #                    help='Usage',
        #                    required=False)

        #parser.add_argument('-o', '--off', type=int)

        args = parser.parse_args()
        valuation_date = parse_date(args.valuation_date)
        print args.bypass
        print args.member
        print args.vendor
        print args.common
        print args.exclude_mbr
        print args.exclude_vendor

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)



if __name__ == '__main__':
        main()
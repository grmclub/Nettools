#!/usr/bin/env python3

import os, sys, getopt
import errno, traceback
import csv
from collections import defaultdict

def parse_fix_line(line: str) -> dict:
    """Parses a single raw FIX line into a key-value dictionary."""
    # Detect delimiter: standard SOH (\x01) or pipe (|)
    delimiter = '\x01' if '\x01' in line else '|'
    fields = {}
    for pair in line.strip().split(delimiter):
        if '=' in pair:
            k, v = pair.split('=', 1)
            fields[k] = v
    return fields

def process_fix_logs(data_file):
    # Aggregators: account -> {'ordered': float, 'filled': float}
    account_stats = defaultdict(lambda: {'ordered': 0.0, 'filled': 0.0})
    seen_new_orders = set()

    for line in data_file:
        tags = parse_fix_line(line)
        msg_type = tags.get('35')
        account = tags.get('1', 'UNKNOWN_ACCOUNT')
        
        # 1. Capture Total Ordered Quantity from New Order Single (35=D)
        if msg_type == 'D':
            cl_ord_id = tags.get('11')
            order_qty = float(tags.get('38', 0))
            
            # Avoid double-counting duplicate order IDs
            if cl_ord_id and cl_ord_id not in seen_new_orders:
                account_stats[account]['ordered'] += order_qty
                seen_new_orders.add(cl_ord_id)

        # 2. Capture Executed Shares from Execution Reports (35=8)
        elif msg_type == '8':
            exec_type = tags.get('150')
            # 1 = Partial Fill, 2 = Fill, F = Trade
            if exec_type in ('1', '2', 'F'):
                last_qty = float(tags.get('32', 0))
                account_stats[account]['filled'] += last_qty

    return account_stats

def print_fill_ratio_report(stats):
    print(f"{'Account':<18} | {'Ordered Qty':<12} | {'Filled Qty':<12} | {'Fill Ratio (%)':<14}")
    print("-" * 62)
    
    for account, data in sorted(stats.items()):
        ordered = data['ordered']
        filled = data['filled']
        ratio = (filled / ordered * 100) if ordered > 0 else 0.0
        
        print(f"{account:<18} | {ordered:<12,.0f} | {filled:<12,.0f} | {ratio:<14.2f}%")

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
            results = process_fix_logs(DATA_FILE)
            print_fill_ratio_report(results)

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" % str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()



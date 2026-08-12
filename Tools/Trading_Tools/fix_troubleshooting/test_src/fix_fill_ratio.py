

#Common Shell Usage Examples
#
#    #Pipe directly from a file:
#    cat fix_messages.log | python fix_fill_ratio.py
#
#    #Filter for specific FIX message types using grep before parsing:
#    grep -E "35=D|35=8" fix_messages.log | python fix_fill_ratio.py
#
#    #Process compressed log files without uncompressing them to disk:
#    zcat fix_messages.log.gz | python fix_fill_ratio.py


import sys
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

def process_fix_stream():
    """Reads FIX messages line-by-line from stdin to keep memory footprint minimal."""
    account_stats = defaultdict(lambda: {'ordered': 0.0, 'filled': 0.0})
    seen_new_orders = set()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

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
    if not stats:
        print("No valid FIX messages processed.")
        return

    print(f"{'Account':<18} | {'Ordered Qty':<12} | {'Filled Qty':<12} | {'Fill Ratio (%)':<14}")
    print("-" * 62)
    
    for account, data in sorted(stats.items()):
        ordered = data['ordered']
        filled = data['filled']
        ratio = (filled / ordered * 100) if ordered > 0 else 0.0
        
        print(f"{account:<18} | {ordered:<12,.0f} | {filled:<12,.0f} | {ratio:<14.2f}%")

if __name__ == "__main__":
    # If stdin is attached to a terminal, alert user on how to pass input
    if sys.stdin.isatty():
        print("Usage: cat fix.log | python fix_fill_ratio.py", file=sys.stderr)
        sys.exit(1)

    results = process_fix_stream()
    print_fill_ratio_report(results)
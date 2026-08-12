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

def process_fix_logs(log_lines):
    # Aggregators: account -> {'ordered': float, 'filled': float}
    account_stats = defaultdict(lambda: {'ordered': 0.0, 'filled': 0.0})
    seen_new_orders = set()

    for line in log_lines:
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


# --- Example Usage ---
if __name__ == "__main__":
    sample_fix_logs = [
        # Account ACC_1: Order 1000 @ 100
        "8=FIX.4.2|35=D|1=ACC_1|11=ORD_001|38=100|",
        # Account ACC_1: Partial fill 40 @ 100
        "8=FIX.4.2|35=8|1=ACC_1|11=ORD_001|150=1|32=40|14=40|",
        # Account ACC_1: Full fill remaining 60 @ 100
        "8=FIX.4.2|35=8|1=ACC_1|11=ORD_001|150=2|32=60|14=100|",
        
        # Account ACC_2: Order 500 @ 200
        "8=FIX.4.2|35=D|1=ACC_2|11=ORD_002|38=200|",
        # Account ACC_2: Partial fill 50 @ 200
        "8=FIX.4.2|35=8|1=ACC_2|11=ORD_002|150=1|32=50|14=50|",
    ]

    results = process_fix_logs(sample_fix_logs)
    print_fill_ratio_report(results)
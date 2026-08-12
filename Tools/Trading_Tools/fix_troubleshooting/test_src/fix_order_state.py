import sys

#cat fix_messages.log | python fix_order_state.py
#

# FIX Tag 39 (OrdStatus) mapping
ORD_STATUS_MAP = {
    '0': 'NEW',
    '1': 'PARTIALLY_FILLED',
    '2': 'FILLED',
    '3': 'DONE_FOR_DAY',
    '4': 'CANCELED',
    '5': 'REPLACED',
    '6': 'PENDING_CANCEL',
    '7': 'STOPPED',
    '8': 'REJECTED',
    '9': 'SUSPENDED',
    'A': 'PENDING_NEW',
    'B': 'CALCULATED',
    'C': 'EXPIRED',
    'E': 'PENDING_REPLACE',
}

SIDE_MAP = {
    '1': 'BUY',
    '2': 'SELL',
    '5': 'SELL_SHORT',
    '6': 'SELL_SHORT_EXEMPT'
}

def parse_fix_line(line: str) -> dict:
    """Parses a single raw FIX string into a key-value dictionary."""
    delimiter = '\x01' if '\x01' in line else '|'
    fields = {}
    for pair in line.strip().split(delimiter):
        if '=' in pair:
            k, v = pair.split('=', 1)
            fields[k] = v
    return fields

def process_fix_stream():
    orders = {}
    id_aliases = {}  # Resolves updated ClOrdID (Tag 11) back to initial order key via OrigClOrdID (Tag 41)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        tags = parse_fix_line(line)
        msg_type = tags.get('35')
        
        # Process New Orders (D), Execution Reports (8), and Cancel Rejects (9)
        if msg_type not in ('D', '8', '9'):
            continue

        cl_ord_id = tags.get('11')
        orig_cl_ord_id = tags.get('41')
        order_id = tags.get('37')

        # Trace primary key through replace/cancel chain (OrigClOrdID -> ClOrdID)
        primary_key = cl_ord_id
        if orig_cl_ord_id and orig_cl_ord_id in id_aliases:
            primary_key = id_aliases[orig_cl_ord_id]
        elif orig_cl_ord_id and orig_cl_ord_id in orders:
            primary_key = orig_cl_ord_id

        if cl_ord_id and primary_key and cl_ord_id != primary_key:
            id_aliases[cl_ord_id] = primary_key

        if not primary_key:
            primary_key = order_id or "UNKNOWN_ORDER"

        # Initialize or update state entry
        if primary_key not in orders:
            orders[primary_key] = {
                'cl_ord_id': cl_ord_id or primary_key,
                'order_id': order_id or 'N/A',
                'account': tags.get('1', 'N/A'),
                'symbol': tags.get('55', 'N/A'),
                'side': SIDE_MAP.get(tags.get('54'), tags.get('54', 'N/A')),
                'order_qty': float(tags.get('38', 0)),
                'cum_qty': float(tags.get('14', 0)),
                'leaves_qty': float(tags.get('151', 0)),
                'avg_px': float(tags.get('6', 0.0)),
                'status_raw': tags.get('39', 'A' if msg_type == 'D' else 'UNKNOWN'),
                'last_update': tags.get('60') or tags.get('52', 'N/A')
            }
        else:
            order = orders[primary_key]
            order['cl_ord_id'] = cl_ord_id or order['cl_ord_id']
            if order_id:
                order['order_id'] = order_id
            if '1' in tags:
                order['account'] = tags['1']
            if '55' in tags:
                order['symbol'] = tags['55']
            if '54' in tags:
                order['side'] = SIDE_MAP.get(tags['54'], tags['54'])
            if '38' in tags:
                order['order_qty'] = float(tags['38'])
            if '14' in tags:
                order['cum_qty'] = float(tags['14'])
            if '151' in tags:
                order['leaves_qty'] = float(tags['151'])
            if '6' in tags:
                order['avg_px'] = float(tags['6'])
            if '39' in tags:
                order['status_raw'] = tags['39']
            if '60' in tags or '52' in tags:
                order['last_update'] = tags.get('60') or tags.get('52')

    return orders

def print_final_state_report(orders):
    if not orders:
        print("No order events found.")
        return

    header = f"{'ClOrdID':<15} | {'OrderID':<12} | {'Account':<10} | {'Symbol':<8} | {'Side':<5} | {'OrderQty':<9} | {'CumQty':<8} | {'LeavesQty':<9} | {'AvgPx':<8} | {'Final Status':<16}"
    print(header)
    print("-" * len(header))

    for key, order in sorted(orders.items()):
        status_desc = ORD_STATUS_MAP.get(order['status_raw'], order['status_raw'])
        print(
            f"{order['cl_ord_id']:<15} | "
            f"{order['order_id']:<12} | "
            f"{order['account']:<10} | "
            f"{order['symbol']:<8} | "
            f"{order['side']:<5} | "
            f"{order['order_qty']:<9,.0f} | "
            f"{order['cum_qty']:<8,.0f} | "
            f"{order['leaves_qty']:<9,.0f} | "
            f"{order['avg_px']:<8.2f} | "
            f"{status_desc:<16}"
        )

if __name__ == "__main__":
    if sys.stdin.isatty():
        print("Usage: cat fix.log | python fix_order_state.py", file=sys.stderr)
        sys.exit(1)

    final_orders = process_fix_stream()
    print_final_state_report(final_orders)
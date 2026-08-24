#!/usr/bin/env python3
import sys
import argparse
from collections import defaultdict

#
# cat fix_messages.log | python3 fix_reconcile.py --client CLIENT_SESSION --broker BROKER_SESSION
# tail -f /path/to/fix.log | python3 fix_reconcile.py --client CLIENT_SESSION --broker BROKER_SESSION
#


def parse_fix_message(line: str) -> dict:
    """Parses a FIX message line into a key-value dictionary.

    Handles SOH (\x01), pipe (|), or space delimiters.
    """
    # Clean string and determine field delimiter
    line = line.strip()
    if not line:
        return {}

    delimiter = None
    for d in ["\x01", "|", " "]:
        if d in line:
            delimiter = d
            break

    if not delimiter:
        return {}

    fields = {}
    for item in line.split(delimiter):
        if "=" in item:
            k, v = item.split("=", 1)
            fields[k.strip()] = v.strip()

    return fields


def parse_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def reconcile_fix_stream(client_session_id: str, broker_session_id: str):
    """Reads FIX messages from stdin and reconciles fills between client and broker sessions."""
    # Data structures: order_id -> {'qty': float, 'value': float, 'count': int}
    client_fills = defaultdict(lambda: {"qty": 0.0, "value": 0.0, "count": 0})
    broker_fills = defaultdict(lambda: {"qty": 0.0, "value": 0.0, "count": 0})

    # Keep track of all encountered order keys across both sides
    all_order_ids = set()

    for line in sys.stdin:
        msg = parse_fix_message(line)

        # We only care about ExecutionReports (35=8)
        if msg.get("35") != "8":
            continue

        sender = msg.get("49", "")
        target = msg.get("56", "")
        exec_type = msg.get("150", "")
        ord_status = msg.get("39", "")

        # Check if the execution report represents a fill/partial fill (ExecType=F/1/2 or CumQty > 0)
        last_qty = parse_float(msg.get("32"))
        last_px = parse_float(msg.get("31"))

        # Skip non-fill execution reports (e.g., Acknowledged, Canceled without fills)
        if last_qty <= 0:
            continue

        # 1. Process Client Session Message
        if client_session_id in (sender, target):
            # Client session matches on Tag 37 (OrderID)
            order_id = msg.get("37")
            if order_id:
                client_fills[order_id]["qty"] += last_qty
                client_fills[order_id]["value"] += last_qty * last_px
                client_fills[order_id]["count"] += 1
                all_order_ids.add(order_id)

        # 2. Process Broker Session Message
        elif broker_session_id in (sender, target):
            # Broker session matches on Tag 11 (ClOrdID)
            order_id = msg.get("11")
            if order_id:
                broker_fills[order_id]["qty"] += last_qty
                broker_fills[order_id]["value"] += last_qty * last_px
                broker_fills[order_id]["count"] += 1
                all_order_ids.add(order_id)

    # Output Reconciliation Summary Table
    print("\n" + "=" * 90)
    print("FIX FILL RECONCILIATION REPORT")
    print("=" * 90)
    header = f"{'Order ID':<20} | {'Status':<12} | {'Client Qty':<10} | {'Broker Qty':<10} | {'Client VWAP':<11} | {'Broker VWAP':<11}"
    print(header)
    print("-" * 90)

    matched, mismatched, missing = 0, 0, 0

    for order_id in sorted(all_order_ids):
        c_data = client_fills.get(order_id, {"qty": 0.0, "value": 0.0, "count": 0})
        b_data = broker_fills.get(order_id, {"qty": 0.0, "value": 0.0, "count": 0})

        c_qty = c_data["qty"]
        b_qty = b_data["qty"]
        c_vwap = (c_data["value"] / c_qty) if c_qty > 0 else 0.0
        b_vwap = (b_data["value"] / b_qty) if b_qty > 0 else 0.0

        # Discrepancy checks
        if c_qty == b_qty and abs(c_vwap - b_vwap) < 1e-5:
            status = "MATCHED"
            matched += 1
        elif c_qty == 0:
            status = "MISSING_CLIENT"
            missing += 1
        elif b_qty == 0:
            status = "MISSING_BROKER"
            missing += 1
        else:
            status = "MISMATCH"
            mismatched += 1

        print(
            f"{order_id:<20} | {status:<12} | {c_qty:<10.2f} | {b_qty:<10.2f} | {c_vwap:<11.4f} | {b_vwap:<11.4f}"
        )

    print("=" * 90)
    print(
        f"TOTAL ORDERS: {len(all_order_ids)} | MATCHED: {matched} | MISMATCHED: {mismatched} | MISSING: {missing}"
    )
    print("=" * 90 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reconcile FIX fills from piped logs."
    )
    parser.add_argument(
        "--client",
        required=True,
        help="SenderCompID or TargetCompID for the client session",
    )
    parser.add_argument(
        "--broker",
        required=True,
        help="SenderCompID or TargetCompID for the broker session",
    )
    args = parser.parse_args()

    reconcile_fix_stream(args.client, args.broker)
#!/usr/bin/env python3
import sys
import argparse
import csv
from collections import defaultdict

#
# generate python code which take fix logs as input from a pipe and gives a reconciliation of fills between a client session and a broker session
# key is order_id tag 37 in the client session is the client order id tag 11 in the broker session
# 
# generate python code which take fix logs as input from a pipe and gives a reconciliation of fills between a client session and a broker session
# key is order_id tag 37 in the client session is the client order id tag 11 in the broker session. Do not add vwap price in the logic 
# script output should produce CSV reports 
# 
# cat fix.log | python3 fix_reconcile.py --client CLIENT_SESSION --broker BROKER_SESSION --csv recon.csv
#


def parse_fix_message(line: str) -> dict:
    """Parses a FIX message line into a key-value dictionary.

    Handles SOH (\x01), pipe (|), or space delimiters.
    """
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


def reconcile_fix_stream(client_session_id: str, broker_session_id: str, csv_output: str = None):
    """Reads FIX messages from stdin and reconciles fill quantities between client and broker sessions."""
    # Data structures: order_id -> {'qty': float, 'count': int, 'exec_ids': set}
    client_fills = defaultdict(lambda: {"qty": 0.0, "count": 0, "exec_ids": set()})
    broker_fills = defaultdict(lambda: {"qty": 0.0, "count": 0, "exec_ids": set()})

    all_order_ids = set()

    for line in sys.stdin:
        msg = parse_fix_message(line)

        # We only care about ExecutionReports (35=8)
        if msg.get("35") != "8":
            continue

        sender = msg.get("49", "")
        target = msg.get("56", "")
        exec_id = msg.get("17", "")
        last_qty = parse_float(msg.get("32"))

        # Skip non-fill execution reports (LastQty <= 0)
        if last_qty <= 0:
            continue

        # 1. Process Client Session Message (Keyed on Tag 37 - OrderID)
        if client_session_id in (sender, target):
            order_id = msg.get("37")
            if order_id:
                client_fills[order_id]["qty"] += last_qty
                client_fills[order_id]["count"] += 1
                if exec_id:
                    client_fills[order_id]["exec_ids"].add(exec_id)
                all_order_ids.add(order_id)

        # 2. Process Broker Session Message (Keyed on Tag 11 - ClOrdID)
        elif broker_session_id in (sender, target):
            order_id = msg.get("11")
            if order_id:
                broker_fills[order_id]["qty"] += last_qty
                broker_fills[order_id]["count"] += 1
                if exec_id:
                    broker_fills[order_id]["exec_ids"].add(exec_id)
                all_order_ids.add(order_id)

    reconciliation_results = []
    matched, mismatched, missing = 0, 0, 0

    for order_id in sorted(all_order_ids):
        c_data = client_fills.get(order_id, {"qty": 0.0, "count": 0, "exec_ids": set()})
        b_data = broker_fills.get(order_id, {"qty": 0.0, "count": 0, "exec_ids": set()})

        c_qty = c_data["qty"]
        b_qty = b_data["qty"]
        qty_diff = c_qty - b_qty

        # Pure quantity-based status check
        if c_qty == b_qty and c_qty > 0:
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

        record = {
            "order_id": order_id,
            "status": status,
            "client_fill_qty": f"{c_qty:.2f}",
            "broker_fill_qty": f"{b_qty:.2f}",
            "qty_diff": f"{qty_diff:.2f}",
            "client_fill_count": c_data["count"],
            "broker_fill_count": b_data["count"],
            "client_exec_ids": ";".join(sorted(c_data["exec_ids"])),
            "broker_exec_ids": ";".join(sorted(b_data["exec_ids"])),
        }
        reconciliation_results.append(record)

    # Print Console Summary Table
    print("\n" + "=" * 75)
    print("FIX FILL RECONCILIATION REPORT (QUANTITY ONLY)")
    print("=" * 75)
    header = f"{'Order ID':<20} | {'Status':<15} | {'Client Qty':<12} | {'Broker Qty':<12} | {'Qty Diff':<10}"
    print(header)
    print("-" * 75)

    for r in reconciliation_results:
        print(
            f"{r['order_id']:<20} | {r['status']:<15} | {float(r['client_fill_qty']):<12.2f} | "
            f"{float(r['broker_fill_qty']):<12.2f} | {float(r['qty_diff']):<10.2f}"
        )

    print("=" * 75)
    print(
        f"TOTAL ORDERS: {len(all_order_ids)} | MATCHED: {matched} | MISMATCHED: {mismatched} | MISSING: {missing}"
    )
    print("=" * 75 + "\n")

    # Export CSV Report
    if csv_output:
        fieldnames = [
            "order_id",
            "status",
            "client_fill_qty",
            "broker_fill_qty",
            "qty_diff",
            "client_fill_count",
            "broker_fill_count",
            "client_exec_ids",
            "broker_exec_ids",
        ]
        with open(csv_output, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reconciliation_results)
        print(f"[+] CSV report written to: {csv_output}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reconcile FIX fill quantities between client and broker sessions."
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
    parser.add_argument(
        "--csv",
        required=False,
        default=None,
        help="Optional path to output CSV file",
    )
    args = parser.parse_args()

    reconcile_fix_stream(args.client, args.broker, csv_output=args.csv)
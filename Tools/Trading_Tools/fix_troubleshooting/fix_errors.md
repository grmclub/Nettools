
### Application & Business Layer Errors
### Application errors occur when session layer framing is valid, but the message payload violates schema constraints or business domain logic.

| Error Type | MsgType | Key Tags | Common Triggers | Resolution |
|--------------|---------|----------|-----------------|------------|
| Session Reject | 35=3 | 371 (RefTagID), 372 (RefMsgType), 373 (SessionRejectReason) | • Missing required conditional tag (e.g., Tag 44 missing on Limit Order)  • Invalid enum value (e.g., 54=9) | Fix message construction logic or update data dictionary. |
| Business Reject | 35=j | 372 (RefMsgType), 380 (BusinessRejectReason), 58 (Text) | • Application functionality disabled for session  • Unsupported message type (e.g., market data request on execution session) | Verify permissions and FIX capabilities with counterparty. |
| Execution Reject | 35=8, 39=8 | 103 (OrdRejReason), 58 (Text) | • Insufficient margin/buying power  • Invalid price/quantity tick size  • Symbol not tradeable | Handle via order management system (OMS) routing rules. |


### Root Causes & Troubleshooting Matrix for Unacknowledged Orders

| Scenario / Root Cause | FIX Diagnostic Signatures | Recovery Action |
|------------------------|---------------------------|----------------|
| **Inbound Sequence Gap** | 35=2 (ResendRequest) issued by venue after order was sent. | Check if venue missed 35=D during sequence replay. Issue Order Status Request (35=H). |
| **Silent Drop by Venue** | Order sent, no 35=8, no session reject, sequence numbers incrementing normally. | Check for custom tag validation failures or network drop on venue side. Contact counterparty support with Tag 11 (ClOrdID) and Tag 34 (MsgSeqNum). |
| **TCP Buffer Drop / Disconnect** | Session disconnected (35=5 or TCP RST) right after sending 35=D. | Reconnect session, check PossDupFlag(43)=Y rules before resending, or query venue state via 35=H. |
| **Corrupted Frame Parsing** | Tag 9 or Tag 10 mismatch caused venue to silently drop packet. | Run frame validator script (`fix_checksum_calc.py`) on raw socket logs. |

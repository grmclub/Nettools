| Error Type                                                    |
| ------------------------------------------------------------- |
|                                                               |
| MsgType                                                       |
|                                                               |
|                                                               |
| Key Tags                                                      |
|                                                               |
|                                                               |
| Common Triggers                                               |
|                                                               |
|                                                               |
| Resolution                                                    |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| Session Reject                                                |
|                                                               |
|                                                               |
| 35=3                                                          |
|                                                               |
|                                                               |
| 371                                                           |
| (RefTagID)                                                    |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| 372                                                           |
| (RefMsgType)                                                  |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| 373                                                           |
| (SessionRejectReason)                                         |
|                                                               |
|                                                               |
| • Missing required                                            |
| conditional tag (e.g., Tag 44 missing on Limit Order)         |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| • Invalid enum                                                |
| value (e.g., 54=9)                                            |
|                                                               |
|                                                               |
| Fix message                                                   |
| construction logic or update data dictionary.                 |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| Business Reject                                               |
|                                                               |
|                                                               |
| 35=j                                                          |
|                                                               |
|                                                               |
| 372                                                           |
| (RefMsgType)                                                  |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| 380                                                           |
| (BusinessRejectReason)                                        |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| 58                                                            |
| (Text)                                                        |
|                                                               |
|                                                               |
| • Application                                                 |
| functionality disabled for session                            |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| • Unsupported                                                 |
| message type (e.g., market data request on execution session) |
|                                                               |
|                                                               |
| Verify permissions and                                        |
| FIX capabilities with counterparty.                           |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| Execution Reject                                              |
|                                                               |
|                                                               |
| 35=8                                                          |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| 39=8                                                          |
|                                                               |
|                                                               |
| 103                                                           |
| (OrdRejReason)                                                |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| 58                                                            |
| (Text)                                                        |
|                                                               |
|                                                               |
| • Insufficient                                                |
| margin/buying power                                           |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| • Invalid                                                     |
| price/quantity tick size                                      |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
|                                                               |
| • Symbol not                                                  |
| tradeable                                                     |
|                                                               |
|                                                               |
| Handle via order                                              |
| management system (OMS) routing rules.                        |
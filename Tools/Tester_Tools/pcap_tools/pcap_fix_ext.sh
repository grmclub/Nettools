#!/bin/bash

## tshark -r input.pcap -Y "fix.msgtype != 0 and fix.msgtype != 1 and fix.msgtype != 'A' and fix.msgtype != '5'" -T fields -e frame.number -e fix.msgtype -e fix.text

##tshark -r dump.pcap \
#-R \'(fix.MsgType[0]=="G" or fix.MsgType[0]=="D" or fix.MsgType[0]=="8" or \ fix.MsgType[0]=="F") and fix.ClOrdID != "0"\' \ 
#-Tfields -Eseparator=, -Eoccurrence=l -e frame.time_relative \
#-e fix.MsgType -e fix.SenderCompID \
#-e fix.SenderSubID -e fix.Symbol -e fix.Side \
#-e fix.Price -e fix.OrderQty -e fix.ClOrdID \
#-e fix.OrderID -e fix.OrdStatus


tshark -r "$1" \
-Y "fix.MsgType == 'D' or fix.MsgType != 'F' or fix.MsgType == 'G' or fix.MsgType == '8' or fix.MsgType == '9' " \
-T fields \
-E header=y \
-E separator='|' \
-Tfields -Eseparator='|' \
-Eoccurrence=l  \
-e frame.time_epoch \
-e fix.MsgType \
-e fix.OrdStatus \
-e fix.SenderCompID \
-e fix.SenderSubID \
-e fix.Symbol \
-e fix.Side \
-e fix.Price \
-e fix.OrderQty \
-e fix.ClOrdID \
-e fix.OrderID 

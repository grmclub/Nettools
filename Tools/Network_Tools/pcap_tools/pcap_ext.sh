#!/bin/bash

tshark -r "$1" \
-T fields \
-E header=y \
-E separator='|' \
-e frame.time \
-e tcp.seq \
-e ip.src \
-e tcp.srcport \
-e ip.dst \
-e tcp.dstport \
-e col.Info

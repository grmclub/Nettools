#!/bin/bash
set -eux


for  file in smbc.pcap mizuho.pcap qhouse.pcap
do
    taskset -c 4 tshark -r ${file} -Tfields  -E separator=',' -e frame.time_epoch -e frame.len > plot.csv
    taskset -c 5 ./itch_plotX.pl -f plot.csv -b > gplot.csv && ./plot_bytes.sh
    mv out.png out_${file}_sec.png

    taskset -c 5 ./itch_plotX.pl -f plot.csv -u > gplot2.csv && ./plot_bytes_us.sh
    mv out.png out_${file}_ms.png
done



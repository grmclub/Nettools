#!/usr/bin/gnuplot
reset
set title 'OUCH latency plot'
set ylabel 'Count'
set xlabel 'Latency (us)'
set datafile separator ","
set grid
set xrange [0:100]
set format x '%10.0f'
set format y '%10.0f'
#set terminal svg size 2311,1506
#set terminal png size 2311,1506
#set terminal svg size 1024,768
set terminal png size 800,600

#set output "out.svg"
set output "out.png"
pl "plot.csv" u 1:2 w impulses t 'Order RTT' 
set terminal X11



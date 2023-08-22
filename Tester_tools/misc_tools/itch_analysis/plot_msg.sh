#!/usr/bin/gnuplot
reset
jst = 32400      #JST time drift 9 hrs
set title 'ITCH Messages'
set ylabel 'messages'
set grid
set xdata time
set timefmt '%s'
set format x '%H:%M:%S'
set format y '%10.0f'
#set terminal svg size 2311,1506
#set terminal png size 2311,1506
set terminal png size 1024,768
#set terminal svg size 1024,768

#set output "out.svg"
set output "out.png"
pl "gplot2.csv" u ($2+jst):1 w impulses t 'msg/sec'
set terminal X11



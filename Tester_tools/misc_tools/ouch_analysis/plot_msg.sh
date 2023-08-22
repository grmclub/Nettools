#!/usr/bin/gnuplot
reset
jst = 32400      #JST time drift 9 hrs
set title 'OUCH Messages'
set ylabel 'messages'
set datafile separator ","
set grid
set xdata time
set timefmt '%s'
set format x '%H:%M:%S'
set format y '%10.0f'
#set terminal svg size 2311,1506
#set terminal png size 2311,1506
#set terminal svg size 1024,768
set terminal png size 800,600

#set output "out.svg"
set output "out_sec.png"
pl "gplot_sec.csv" u ($1+jst):2 w impulses t 'messages/sec'
set terminal X11



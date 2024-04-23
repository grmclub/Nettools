#!/usr/bin/gnuplot
reset
jst = 32400      #JST time drift 9 hrs
set title 'ITCH Bandwidth analysis'
set ylabel 'bits/sec'
set grid
set xdata time
set timefmt '%s'
set format x '%H:%M:%S'
set format y '%10.0f'
#set terminal svg size 2311,1506
#set terminal png size 2311,1506
set terminal png size 1528,1288
#set terminal svg size 1024,768

#set output "out.svg"
set output "out.png"
#pl "gplot.csv" u ($1+jst):2 w impulses t 'sec', '' u ($1+jst):3 w impulses t 'usec'
pl "gplot2.csv" u ($1+jst):3 w impulses t '1 ms', \
             '' u ($1+jst):2 w impulses t '1 sec'
#pl "gplot.csv" u ($1+jst):3 w impulses t 'usec'
set terminal X11



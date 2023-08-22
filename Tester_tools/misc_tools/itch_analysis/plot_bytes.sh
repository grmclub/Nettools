#!/usr/bin/gnuplot
reset
jst = 32400      #JST time drift 9 hrs
set title 'Bandwidth analysis'
set ylabel 'bits/sec'
set grid
set xdata time
set timefmt '%s'
set format x '%H:%M:%S'
set format y '%10.0f'
#set terminal svg size 2311,1506
set terminal png size 2311,1506
#set terminal svg size 1024,768

#set output "out.svg"
set output "out.png"
pl "gplot.csv" u ($1+jst):2 w impulses t 'bits'
set terminal X11



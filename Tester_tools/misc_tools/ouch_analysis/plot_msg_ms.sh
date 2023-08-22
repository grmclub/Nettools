#!/usr/bin/gnuplot
reset
jst = 32400      #JST time drift 9 hrs
set title 'OUCH messages'
set ylabel 'messages'
set datafile separator ","
#set logscale y
#set ytics 200
set grid
set xdata time
set timefmt '%s'
set format x '%H:%M:%S'
set format y '%10.0f'
set style fill solid
#set terminal svg size 2311,1506
#set terminal png size 2311,1506
#set terminal png size 1528,1288
set terminal png size 1024,768
#set terminal png size 800,600

#set output "out.svg"
set output "out_ms.png"
#pl "gplot.csv" u ($1+jst):2 w impulses t 'sec', '' u ($1+jst):3 w impulses t 'usec'
#pl "gplot_us.csv" u ($1+jst):3 w impulses t '1 ms', \
#             '' u ($1+jst):2 w impulses t '1 sec'

pl "gplot_ms.csv" u ($1+jst):3 w impulses t '1 ms', \
               '' u ($1+jst):2 w impulses t '1 sec'

#pl "gplot.csv" u ($1+jst):3 w impulses t 'usec'
set terminal X11



#!/usr/bin/gnuplot
set term pngcairo size 1280,640;

if (!exists("resource")) resource = "steel";
fn = sprintf("%s.csv", resource);
print(fn)

set out sprintf("%s.png", resource);
set datafile separator ",";
set timefmt "%Y-%m-%d %H:%M:%S";

set title sprintf("Price history of %s", resource);

set xlabel "date";
set xdata time;
set format x "%d/%m\n%H:%M"

set ylabel "price";
set grid;

plot fn u 1:2 with lp title "highest buy", \
     fn u 1:4 with lp title "average", \
     fn u 1:5 with lp title "lowest sell";

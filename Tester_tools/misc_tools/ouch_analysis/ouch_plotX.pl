#!/usr/bin/perl
#
#Ouch bandwidth analysis
# It is millisecond bandwidth projected to seconds interval.
#
#  find . -name '*.bz2' -print0 | xargs -0 -I {} -P 6 bunzip2 {}
#  taskset -c 4 tcpslice *.tcpdump | tcpdump -r - "host $IP  or (vlan and host $IP) " -w xx.pcap
#
#  taskset -c 4 tshark -r Ouch-pri.pcap -Tfields  -E separator=',' -e frame.time_epoch -e frame.len > plot.csv
#  taskset -c 4 ./ouch_plotX.pl -f plot.csv -b > gplot.csv && ./plot_bytes.sh && eog out.png
#  taskset -c 4 ./ouch_plotX.pl -f plot.csv -u > gplot.csv && ./plot_bytes_us.sh && eog out.png
#
#Message counter
#  --does not count multiple msg's in a packet
#  taskset -c 4 tshark -r xx.pcap -Tfields  -E separator=',' -e frame.time_epoch -e ouch.message_type > plot.csv
#  taskset -c 4 ./ouch_plotX.pl -f plot.csv -m > gplot_sec.csv && ./plot_msg.sh && eog out_sec.png
#  taskset -c 4 ./ouch_plotX.pl -f plot.csv -M > gplot_us.csv && ./plot_msg_us.sh && eog out_us.png
#

use Getopt::Std;
#use autodie qw /:all/;
use Carp;
use Encode;
use POSIX qw(strftime);
use Time::HiRes qw(sleep);
use Term::ANSIColor qw(:constants);

use strict;
use warnings;

my $g_fname;
my $g_delim;

my ($g_sec_sum, $g_ms_sum);
my ($g_ms_max);
my ($g_tm_sec_group, $g_tm_ms_group);
my %args;

$SIG{'INT'} = "shutdown";
$SIG{'TERM'} = "shutdown";

sub shutdown {
    print "\n\nCaught Interrupt, Terminating...\n";
    exit(1);
}

sub reset_counters {
    $g_sec_sum  = 0;
    $g_ms_sum = 0;
    $g_ms_max = 0;
}

sub ms_counter {
    my $tm_curr_sec = shift;
    my $bits        = shift;

    if ($g_tm_ms_group == $tm_curr_sec) {
        $g_ms_sum = $g_ms_sum + $bits;
    }
    else {
        $g_tm_ms_group = $tm_curr_sec;

        if ($g_ms_max < $g_ms_sum) {
            $g_ms_max = $g_ms_sum;
        }
        $g_ms_sum = 0;
    }
}

sub bw_analysis {

    my $bits    = 0;
    my $tm_sec  = "";
    my $tm_ms = "";
    my $flag    = 0;

    open(my $fh, '<', $g_fname) or
        Carp::croak("Failed to create file : $g_fname $! !");

    while (my $line = <$fh>) {
        #chomp $line;
        my @fields = split ($g_delim, $line);

        $tm_sec  = int($fields[0]);
        $tm_ms = int($fields[0]*1000);

        #convert bytes into bits
        $bits    = int($fields[1])*8;
        #print "$tm_sec, $tm_ms -- $bits \n";

        if($flag == 0 ) {
            $g_tm_sec_group  = $tm_sec;
            $g_tm_ms_group = $tm_ms;
            reset_counters();
            $flag = 1;
        }

        if ($g_tm_sec_group == $tm_sec) {
            ms_counter($tm_ms, $bits);
            $g_sec_sum = $g_sec_sum + $bits;
        }
        else {
            printf("%ld %ld %ld\n", $g_tm_sec_group, $g_sec_sum, ($g_ms_max*1000));
            $g_tm_sec_group = $tm_sec;
            reset_counters();
        }
    }
    close($fh);

    #last iteration
    printf("%ld %ld %ld\n", $g_tm_sec_group, $g_sec_sum, ($g_ms_max*1000));
}

sub bw_analysis_sec {

    my $sum   = 0;
    my $tm_group = "";
    my $flag  = 0;

    open(my $fh, '<', $g_fname) or
        Carp::croak("Failed to create file : $g_fname $! !");

    while (my $line = <$fh>) {
        #chomp $line;
        my @fields = split ($g_delim, $line);
        $fields[0] = substr($fields[0], 0,10);
        #print $fields[0]. "--".$fields[1]."\n";

        if($flag == 0 ) {
            $tm_group = $fields[0];
            $flag = 1;
        }

        if ($tm_group eq $fields[0]) {
            #convert bytes into bits
            $sum = $sum + int($fields[1])*8;
        }
        else {
            printf("%s %d\n", $tm_group, $sum);
            $tm_group = $fields[0];
            $sum = 0;
        }
    }
    close($fh);

    #last iteration
    printf("%s %d\n", $tm_group, $sum);
}

sub msg_analysis {

    my $sum = 0;
    my $ts = 0;
    my $tm_current = 0;
    my $tm_group = 0;
    my $flag = 0;

    open(my $fh, '<', $g_fname) or
        Carp::croak("Failed to create file : $g_fname $! !");

    while (my $line = <$fh>) {
        my @fields = split ($g_delim, $line);
        $tm_current = substr($fields[0], 0,10);

        #print "$tm_current -- $fields[0] -- $g_delim \n";exit;

        if($flag == 0 ) {
            $tm_group = $tm_current;
            $flag = 1;
        }

        if ($tm_group eq $tm_current) {
            ++$sum;
        }
        else {
            printf("%s,%d\n", $tm_group, $sum);
            $sum = 0;
            $tm_group = $tm_current;
        }
    }
    close($fh);

    #last iteration
    printf("%s,%d\n", $tm_group, $sum);
}

sub msg_analysis_us {

    #my $msg    = 0;
    my $tm_sec = "";
    my $tm_ms  = "";
    my $flag   = 0;

    open(my $fh, '<', $g_fname) or
        Carp::croak("Failed to create file : $g_fname $! !");

    while (my $line = <$fh>) {
        #chomp $line;
        my @fields = split ($g_delim, $line);

        $tm_sec  = int($fields[0]);
        $tm_ms = int($fields[0]*1000);

        #convert bytes into msg
        #$msg    = int($fields[1]);
        #print "$tm_sec, $tm_ms -- $msg \n";

        if($flag == 0 ) {
            $g_tm_sec_group  = $tm_sec;
            $g_tm_ms_group = $tm_ms;
            reset_counters();
            $flag = 1;
        }

        if ($g_tm_sec_group == $tm_sec) {
            ms_counter($tm_ms, 1);
            ++$g_sec_sum;
        }
        else {
            #printf("%ld %ld %ld\n", $g_tm_sec_group, $g_sec_sum, ($g_ms_max*1000));
            printf("%ld,%ld,%ld\n", $g_tm_sec_group, $g_sec_sum, ($g_ms_max));
            $g_tm_sec_group = $tm_sec;
            reset_counters();
        }
    }
    close($fh);

    #last iteration
    #printf("%ld %ld %ld\n", $g_tm_sec_group, $g_sec_sum, ($g_ms_max*1000));
    printf("%ld,%ld,%ld\n", $g_tm_sec_group, $g_sec_sum, ($g_ms_max));
}




sub init {
    $g_fname = "./plot.csv";
    $g_delim = ",";
}

sub main {

    getopts("hd:f:bmMs:u", \%args);

    if ( $args{h} ) {
        print BOLD,GREEN,"";
        printf "$0: \n";
        print "\t-f <path/filename>\n";
        print "\t-b Bandwidth Analysis(sec)\n";
        print "\t-u Bandwidth Analysis in (ms)\n";
        print "\t-m Msg Throughput summary \n";
        print "\t-M Msg Throughput summary(us) \n";
        print "\t-s<|> Msg delimeter \n";
        print RESET;
        exit(0);
    }

    init();

    if ( $args{d} ) {
        $g_delim = $args{d};
    }

    if ( $args{f} ) {
        $g_fname = $args{f};
    }

    if ( $args{s} ) {
        $g_delim = $args{s};
    }

    if ( $args{b} ) {
        bw_analysis_sec();
        exit(0);
    }

    if ( $args{u} ) {
        bw_analysis();
        exit(0);
    }

    if ( $args{m} ) {
        msg_analysis();
        exit(0);
    }

    if ( $args{M} ) {
        msg_analysis_us();
        exit(0);
    }
}

main();

1;

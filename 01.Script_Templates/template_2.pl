#!/usr/bin/perl

use Getopt::Std;
#use autodie qw /:all/;
use Carp;
use Encode;
use POSIX qw(strftime);
use Time::HiRes qw(sleep);


use strict;
use warnings;

my $g_host     = 'dxx01x';
my $g_port_out = 5002;
my $g_port_in  = 5012;
my $g_socket_out;
my $g_socket_in;
my %args;

$SIG{'INT'} = "shutdown";
$SIG{'TERM'} = "shutdown";

sub shutdown {
    print "\n\nCaught Interrupt, Terminating...\n";
    exit(1);
}

sub main{

    getopts("Hh:i:o:", \%args);

    if ( $args{H} ) {
        printf "$0 -h <host> -i <IN_PORT> -o <OUT_PORT>";
        exit(0);
    }

    my $sum = 0;
    my $group = "";
    my $fname = "./plot.csv";
    open(my $fh, '<', $fname) or
        Carp::croak("Failed to create file : $fname $! !");

    while (my $line = <$fh>) {
        chomp $line;
        my @fields = split ("," , $line);
        $fields[0] = substr($fields[0], 0,10);
        #print $fields[0]. "--".$fields[1]."\n";

        if ($group eq $fields[0]) {
            $sum = $sum + int($fields[1]);
        }
        else {
            printf("%s %d\n", $group, $sum);
            $group = $fields[0];
            $sum = 0;
        }
    }
    close($fh);
}

main();


1;

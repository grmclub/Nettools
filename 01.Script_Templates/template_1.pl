#!/usr/bin/perl

use Getopt::Std;
#use autodie qw /:all/;
use Carp;
use Encode;
use POSIX qw(strftime);
use Time::HiRes qw(sleep);
use Term::ANSIColor qw(:constants);

use strict;
use warnings;

my $g_NEW_count = 0;

my $today = POSIX::strftime("%Y%m%d",localtime);
my $g_fname = "file_$today.log";
my %args;

$SIG{'INT'} = "shutdown";
$SIG{'TERM'} = "shutdown";

sub shutdown {
    print "\n\nCaught Interrupt, Terminating...\n";
    exit(1);
}

sub main {

    getopts("hf:", \%args);

    if ( $args{h} ) {
        printf "$0 -f <path/filename>\n";
        exit(0);
    }

    if ( $args{f} ) {
        $g_fname = $args{f};
    }
}

main();
1;

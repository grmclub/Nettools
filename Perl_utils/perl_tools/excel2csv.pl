#!/usr/bin/perl -w

use Getopt::Std;
#use autodie qw /:all/;
use Carp;
use Encode;
use POSIX qw(strftime);
use Time::HiRes qw(sleep);
use Spreadsheet::ParseExcel;

##Reference adapted from
#https://metacpan.org/pod/Spreadsheet::ParseExcel

use strict;
use warnings;

my $filename =""

sub convert_xls
{
    my ($fiename)= @_;
    my $parser   = Spreadsheet::ParseExcel->new();
    my $workbook = $parser->parse(filename);
     
    if ( !defined $workbook ) {
        die $parser->error(), ".\n";
    }
     
    for my $worksheet ( $workbook->worksheets() ) {
     
        my ( $row_min, $row_max ) = $worksheet->row_range();
        my ( $col_min, $col_max ) = $worksheet->col_range();
     
        for my $row ( $row_min .. $row_max ) {
            for my $col ( $col_min .. $col_max ) {
     
                my $cell = $worksheet->get_cell( $row, $col );
                next unless $cell;
     
                print "Row, Col    = ($row, $col)\n";
                print "Value       = ", $cell->value(),       "\n";
                print "Unformatted = ", $cell->unformatted(), "\n";
                print "\n";
            }
        }
    }       
}

sub main {
    getopts("hf:", \%args);

    if ( $args{h} ) {
        printf "$0 -f <path/filename>\n";
        exit(0);
    }

    if ( $args{f} ) {
        $filename = $args{f};
        convert_xls($filename);
    }
}

main();
1;




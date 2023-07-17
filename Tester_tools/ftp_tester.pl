#!/usr/bin/perl

use Getopt::Std;
use POSIX qw /strftime/;
use Net::FTP;

my $host = "dev";
my $username = "me";
my $password = "secret";
my $ftpdir = "XXX";
my $file = sprintf("XXX_%d.xml.zip","20150408");

sub connect_and_get_data
{
    #-- connect to ftp server
    #my $ftp = Net::FTP->new($host) or die "Error connecting to $host: $!";
    my $ftp = Net::FTP->new($host, Timeout => 5, Debug   => 1) or die "Error connecting to $host: $!";

    #-- login
    $ftp->login($username,$password) or die "Login failed: $!";

    #-- chdir to $ftpdir
    #$ftp->dir($ftpdir) or die "Can't go to $ftpdir: $!";

    #-- download file
    $ftp->binary() or die "Can't switch to binary mode: $!";
    $ftp->get("$ftpdir/$file", "$file") or die "Can't get $file: $!";

    #-- close ftp connection
    $ftp->quit or die "Error closing ftp connection: $!";
}

sub main {

    getopts("hd:", \%args);

    if ( $args{h} ) {
        printf "$0 -d date(YYYYMMDD)\n";
        exit(0);
    }

    if ( $args{d} ) {
        my $g_date = $args{d};
        $file = sprintf("XXX_%d.xml.zip", $g_date);
    }

    &connect_and_get_data();
}

&main();
1;


#.!/usr/bin/perl -w

use lib @/lib/common/perl/modles/lib/perl5/site_perl/5.8.5/"

use strict
#use warnings

ue Getopt::Std;
use FileHandle;
use MImE::Lite;
use Data::Dumper;
use POSIX qw(strftime);
use Spreadsheet::WriteExcel
use Spreadsheet::ParseExcel;

my $g_filename="";

sub convert_xls
{
my ($filename)= @_;
my $parser=Spreadsheet::ParseExcel->new();
my $workbook=$parser-parse($filename);

if(!defined $workbook) {
	die*parser->error(), "\n";
}

my $line;
for my $worksheet ($workbook->worksheets()) {
my ($row_min,$row_max) =$worksheet->row_range();
my ($col_min,$col_max) =$worksheet->col_range();
for my $row($row_min .. $row_max) {
$line="";
for my $col($col_min .. $col_max) {
my $cell= $worksheet->get_cell$row,$col);
next unless $cell;
$line = $line .$cell->unformated() . ";";
#print "Row,Col = ($row,$col), "\n";
#print "Value =, cell->value();
# print '$line \n";

}
print '$line \n";
}

}

sub main
{
getopts("hf:", \my %args);

if($args{h}){
	printf "$0 -f <file.xls";
}

if($args{f}){
	$g_filename = args{f};
	convert_xls($g_filename);
}

}

main();
1;

#!/usr/bin/perl

# --Filter Pri/Sec  Mold Feed
#ip="239.72.1.2" / ip="239.72.2.2"
#
# --To pre Filter
# taskset -c 5 tcpslice *.tcpdump | tcpdump -r - "host 239.72.1.2  or (vlan and host 239.72.1.2) " -w itch-pri.pcap
#
# --Extract Seqno
#tcpslice *.tcpdump | tshark -nr - \
#    -Y "ip.addr == 239.72.1.2" \
#    -Tfields \
#    -e frame.time_epoch \
#    -e moldudp64.sequence \
#    -e moldudp64.count \
#    -e itch.message_type
#
# taskset -c 5 \
# tshark -r imc.pcap -Y "ip.addr == 239.72.1.2" -Tfields  -e frame.time_epoch -e moldudp64.sequence -e moldudp64.count -e itch.message_type
#

use Getopt::Std;
use Data::Dumper;

use strict;
use warnings;

my %args;
my $g_filename;
my $scriptName = "check_seq_gap.pl";

getopts("hf:", \%args);

if ( $args{f} ) {
    $g_filename = $args{f};
    if (-e $g_filename) {
        ### process File
        &ProcessFile();
    }
    else {
        die( "File $g_filename does not exists!");
    }
}

elsif ( $args{h} ) {
    &usage();
}

else{
    &usage();
}


sub usage(){
    print ("\nUsage: $scriptName -h for Usage");
    print ("\nUsage: $scriptName -f filename.");
    exit 0;
}

sub trim
{
    my $string = shift;
    $string =~ s/^\s+//;
    $string =~ s/\s+$//;
    return $string;
}


sub ProcessFile()
{
    my $seq_cnt  = 0;
    #my $f_time   = 0;
    #my $f_rseq   = 0;
    #my $count  = 0;
    #my $f_mtype  = 0;

    open my $fh, '<', $g_filename
        or die "Error opening $g_filename - $!\n";

    while (my $line = <$fh>) {
        my ($f_time, $f_rseq, $count, $f_mtype) = split('\t', $line);
        $f_rseq = &trim($f_rseq);
        $f_mtype = &trim($f_mtype);

        if($f_mtype eq "" || $f_rseq eq ""){
            next;
        }
        #print "Processed Line: $f_time :". length($f_rseq) .": MsgType: $f_mtype\n";
        #next;

        ##Initialize counter
        if ($seq_cnt == 0) {
            print "Set initial seq no.\n";
            $seq_cnt = $f_rseq;
        }

        if ($seq_cnt != $f_rseq) {
            print  " Sequence Gap Time: $f_time"
                  ." Expected: $seq_cnt"
                  ." RecvSeq: $f_rseq"
                  ."\n";

            $seq_cnt = $f_rseq;
        }

        if ($count > 1) {
            $seq_cnt = $seq_cnt + $count;
        }
        else {
            ++$seq_cnt;
        }

    }
}

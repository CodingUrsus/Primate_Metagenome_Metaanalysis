#!/usr/bin/perl

# This script parses diamond output files
# ASSUMES THE FOLLOWING COLUMN ORDER
#  1. qseqid: query sequence ID
#  2. sseqid: database sequence ID
#  3. qlen: query sequence length
#  4. slen: database sequence length
#  5. length: length of alignment
#  6. qstart: start of alignment in query
#  7. qend: end of alignment in query
#  8. sstart: start of alignment in database seq
#  9. send: end of alignment in database seq
#  10. pident: percent identity
#  11. gaps: number of gaps
#  12. evalue: expect value
#  13. bitscore: bit score
#
# The output is a file to input to MCL
# only includes 3 columns

use strict;
use warnings;
use Getopt::Long;
use POSIX qw/strftime/;

my $usage = "Usage: $0 --in <file> 
		in       : diamond output file.
		complete : tab delim file with first column ID of complete proteins. 
		redund   : txt file with IDs of redundant proteins.
		ecut     : (default 1e-10)evalue cutoff, only keep eval below cutoff.
		covcut   : (default 0.8)coverage cutoff, must cover at least this prop of BOTH seq.
		metric   : (default pident)metric to report in output (opts:pident,eval,bitscore).
		out      : output file.";

my ($infile,$complete,$redund,$outfile);
my $ecut=1e-10;
my $covcut=0.8;
my $metric="pident";
GetOptions("in=s"       => \$infile,   #input file path
           "complete=s" => \$complete, #complete protein list
	   "redund=s"   => \$redund,   #redundant list
	   "ecut=i"     => \$ecut,     #evalue cutoff
	   "covcut=i"   => \$covcut,   #coverage cutoff
	   "metric=s"   => \$metric,   #metric to report
	   "out=s"      => \$outfile   #output filename
) or die "$usage\n";

if(!$infile || !$complete || !$redund || !$outfile){
	die "$usage\n";
}

my $starttime= strftime('%Y-%m-%d %H:%M:%S',localtime);
print "Starting $infile: $starttime\n";
$starttime=time();

#get host and DB names
my @filepath = split(/\//,$infile);
print $filepath[$#filepath],"\n";

my @fileparts = split(/_|\./,$filepath[$#filepath]);
my $hostid = $fileparts[0];
my $dbid   = $fileparts[1];
if($dbid eq "KEGG"){
	die("unwanted database: $dbid\n");
}

print "*** Parameters***\n";
print "HostID: $hostid\n";
print "DatabaseID: $dbid\n";
print "Evalue cutoff: $ecut\n";
print "Coverage cutoff: $covcut\n";
print "Reporting metric: $metric\n";
print "********************\n";

my $cstart=time();
print "initializing complete protein hash\n";
open(COMP,"<",$complete) || die "cannot open $complete\n";
my %comp_hash;
while (my $line=<COMP>){
	chomp $line;
	my @lineparts = split(/\s/,$line);
	my $comp_id = $lineparts[0];
	$comp_id =~ s/^>//; # get rid of beginning carrot in human ids
	#print $comp_id,"*\n";
	$comp_hash{$comp_id}="";
}
close(COMP);
print "DONE\n";
my $cdone=time;
my $cdiff=$cdone-$cstart;
print "Time elapsed: $cdiff seconds\n";
print "********************\n";

my $rstart=time();
print "initializing redundant protein hash\n";
open(REDUND,"<",$redund) || die "cannot open $redund\n";
my %redund_hash;
while (my $redund_id=<REDUND>){
	chomp $redund_id; 
	$redund_hash{$redund_id}="";
	#print $redund_id,"\n";
}
close(REDUND);
print "DONE\n";
my $rdone=time();
my $rdiff=$rdone-$rstart;
print "Time elapsed: $rdiff seconds\n";
print "********************\n";

print "parsing input\n";
open(IN,"<",$infile) || die "cannot open $infile\n";
open(OUT,">",$outfile) || die "cannot open $outfile\n";

my @counts=(0,0,0,0,0);
while(my $line=<IN>){
	chomp $line;
	my ($qseqid, $sseqid, $qlen, $slen, $length, $qstart, $qend, $sstart, $send, $pident, $gaps, $evalue, $bitscore) = split(/\t/,$line);
	
	#eliminate self matches
	if($qseqid eq $sseqid){
		#print "self match, skipping $qseqid $sseqid\n";
		$counts[0]=$counts[0]+1;
		next;
	}
	
	#adjust evalue and eliminate eval above cutoff
	my $dbsize = 14473088278; #letters
	my $adj_evalue = $qlen*$dbsize*(2**(-1*$bitscore));
	if($adj_evalue > $ecut){
		#print "fails eval cutoff, skipping $qseqid $sseqid\n";
		$counts[1]=$counts[1]+1;
		next;
	}
	
	#get coverage of sequences
	my $qcov = $length/$qlen;
	my $scov = $length/$slen;
	
	#eliminate coverage below cutoff
	if($qcov <= $covcut){
		#print "q fails cov cutoff, skipping $qseqid\n";
		$counts[2]=$counts[2]+1;
		next;
	}
	if($scov <= $covcut){
		#print "s fails cov cutoff, skipping $sseqid\n";
		$counts[2]=$counts[2]+1;
		next;
	}
	
	#eliminate redundant proteins
	if(exists($redund_hash{$qseqid})){
		#print "$qseqid is redundant, skipping\n";
		$counts[3]=$counts[3]+1;
		next;
	}
	if(exists($redund_hash{$sseqid})){
		#print "$sseqid is redundant, skipping\n";
		$counts[3]=$counts[3]+1;
		next;
	}
	
	#print "***$qseqid-$sseqid***\n";
	#only write out matches between complete proteins
	if(exists($comp_hash{$qseqid})){
		#print "$qseqid complete\n";
		if(exists($comp_hash{$sseqid})){
			#print "$sseqid complete\n";
			if($metric eq "pident"){
				#print "$qseqid\t$sseqid\t$pident\n";
				print OUT "$qseqid\t$sseqid\t$pident\n";
			}else{
				die "unsupported metric\n";
			}
		}else{
			#print "$sseqid not complete, skipping\n";
			$counts[4]=$counts[4]+1;
			next;
		}	
	}else{
		#print "$qseqid not complete, skipping\n";
		$counts[4]=$counts[4]+1;
		next;
	}
}

close(IN);
close(OUT);

my $total = $counts[0]+$counts[1]+$counts[2]+$counts[3]+$counts[4];
print "Total excluded matches: $total\n";
print "selfmatch: $counts[0]\n";
print "high eval: $counts[1]\n";
print "lower cov: $counts[2]\n";
print "redundant: $counts[3]\n";
print "incomplet: $counts[4]\n";

my $endtime=strftime('%Y-%m-%d %H:%M:%S',localtime);
print "DONE: $endtime\n";
$endtime=time();

my $diff=$endtime-$starttime;
print "Total time elapsed: $diff seconds\n";
print "--------------------------------\n";


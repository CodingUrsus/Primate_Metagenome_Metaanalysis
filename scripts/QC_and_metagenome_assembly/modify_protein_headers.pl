#!/usr/bin/perl

### USAGE: perl scripts/modify_protein_headers.pl --in <infile_proteins.faa> --out <outfile.faa> 
#		--host <host ID to add to header> --type <either c(my data) or p (public data)>
#		--mapping <name of mapping file.txt>

use strict;
use warnings;
use Getopt::Long;

my $infile;
my $outfile;
my $host;
my $type;
my $mapping;
GetOptions("in=s"      => \$infile, 
           "out=s"     => \$outfile,
	   "host=s"    => \$host,
	   "type=s"    => \$type,
	   "mapping=s" => \$mapping)  
or die "Usage: $0 --in --out --host --type --mapping\n";

if(!$infile || !$outfile || !$host || !$type || !$mapping){
	die "Usage: $0 --in --out --host --type --mapping\n";
}

if($type !~ /c|p|a/){
	die "unrecognized type: $type\n";
}

open(IN,"<",$infile)||die("cannot open $infile");
open(OUT,">",$outfile);
open(MAP,">",$mapping);

while(my $line = <IN>){
	chomp $line;
	if($line =~ /^>/){
		my @header_parts = split(' ',$line);
		#print $header_parts[0],"\n";
		my @id_parts = split(/_/,$header_parts[0],2);
		my $new_header =  ">".$host."_".$type."_".$id_parts[1];
		#print $new_header,"\n";
		print OUT $new_header,"\n";

		$new_header =~ s/>//;
		my $old_header = $header_parts[0];
		$old_header =~ s/>//;
		$line =~ s/>//;
		print MAP $new_header,"\t",$old_header,"\t",$line,"\n";
	}else{
		print OUT $line,"\n";
	}
}
close(IN);
close(OUT);
close(MAP);

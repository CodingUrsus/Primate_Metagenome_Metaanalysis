#!/usr/bin/perl

######################
#                    #
# run_shotcleaner.pl #
#                    #
######################

use strict; 
use warnings; 
use File::Basename;
use Getopt::Long;
#use IO::Zlib;


#my $indir = "/ssd/hammera/SRA_files/sra/";
#my $outdir = "/ssd/hammera/IGC/Bacu/processed/"; 
#my $nprocs = 35;
#my $db = "/ssd/hammera/IGC/Bacu/bt_index/";
#my $dbname = "Bacu";
my $adapt_trim = 0;
my $ad_path    = "/raid1/home/micro/gaulkec/bin/shotcleaner/pkg/Trimmomatic-0.35/adapters/NexteraPE-PE.fa";
my $se         = 1;
my $both       = 0;  
#both only works for adaptor trimming set (i.e., --at) 

GetOptions ("indir=s"  => \my $indir,    
			"nprocs=i" => \my $nprocs,   
			"outdir=s" => \my $outdir,
			"db=s"     => \my $db,
			"dbname=s" => \my $dbname,
			"at"       => \$adapt_trim,
			"ad_path"  => \$ad_path,
			"se"       => \$se,
			"both"     => \$both)
			 
or die("Error in command line arguments\n");
die("--indir not defined") unless defined($indir);
die("--outdir not defined") unless defined($outdir);

my @suffixlist = qw(
	.fq
	.fastq
	.fq.gz
	.fastq.gz
	); 



my $count = 1;

if($adapt_trim){
	my $file_hash = get_files($indir);
	foreach my $key (keys %$file_hash){		
		my $ndir = "$outdir$count";
		mkdir $ndir;
		if($both){
			system("perl /home/micro/sharptot/src/shotcleaner/shotcleaner.pl -1 $indir/$file_hash->{$key}->{R1} -2 $indir/$file_hash->{$key}->{R2} -o $ndir -d $db -n $dbname --nprocs $nprocs --adapt-path $ad_path, --filter bowtie2,bmtagger");
			$count = $count + 1;
		}else{
			system("perl /home/micro/sharptot/src/shotcleaner/shotcleaner.pl -1 $indir/$file_hash->{$key}->{R1} -2 $indir/$file_hash->{$key}->{R2} -o $ndir -d $db -n $dbname --nprocs $nprocs --adapt-path $ad_path");
			$count = $count + 1;
		}	
	}
}elsif($se){
	my @files = get_files_se($indir); 
	foreach my $file(@files){
		my $ndir = "$outdir$count";
		mkdir $ndir;
		system("perl /home/micro/sharptot/src/shotcleaner/shotcleaner.pl -1 $indir/$file -o $ndir -d $db -n $dbname --nprocs $nprocs");
		$count = $count + 1;
	}
}else{
	my $file_hash = get_files($indir);
	foreach my $key (keys %$file_hash){ 
		print "$indir/$file_hash->{$key}->{R1}\n$indir/$file_hash->{$key}->{R2}\n\n\n";
		my $ndir = "$outdir$count";
		mkdir $ndir;
		system("perl /home/micro/sharptot/src/shotcleaner/shotcleaner.pl -1 $indir/$file_hash->{$key}->{R1} -2 $indir/$file_hash->{$key}->{R2} -o $ndir -d $db -n $dbname --nprocs $nprocs");
		$count = $count + 1;
	}
}


####subroutines 

sub get_files_se {
	my ($dir) = @_; 
	opendir(DIR1, $dir) or die $!;
	my @files;

	while ( my $file = readdir(DIR1) ){
	
		if ( $file =~ m/^\./ ) {
			next; 
		}elsif ( $file !~ m/\.fastq/ ){
			next;
		}else{
			push ( @files, $file );
		}
	}
	close(DIR1); 
	return @files; 
}	

sub get_files {
	my ($dir) = @_; 
	opendir(DIR1, $indir) or die $!;

	my @files;

	while ( my $file = readdir(DIR1) ){
	
		if ( $file =~ m/^\./ ) {
			next; 
		}elsif ( $file !~ m/\.fastq/ ){
			next;
		}else{
			push ( @files, $file );
		}
	}
	close(DIR1); 

	my $file_hash; 

	foreach my $file (@files){
		chomp $file;
		my @sfile = split(/\_/, $file);
		my $id   = $sfile[0];
		my @ids  = split(/\-/, $id);
		my $sid  = $ids[1];
		my $rnum;
		if( $file =~ m/\_R2\_/ ){
			$rnum = "R2";
		}else{
			$rnum = "R1";
		}
		$file_hash->{$sid}->{$rnum} = $file;
	}
	return $file_hash
}

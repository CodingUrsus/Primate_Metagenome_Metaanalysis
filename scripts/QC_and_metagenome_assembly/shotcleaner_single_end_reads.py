#!/usr/bin/env python

## Here's what this script does:
# 1. Build a bowtie db and name it for the taxa in question
# 2. Hit it with shotcleaner
## Special note, this script relies on a very specific _R2_ pattern for sample partitioning, so there needs to be a rename function as well
# 3. Get the R1 and R2 files from the shotcleaner output
# 4. Format the files and roll with megahit
# 5. Hit it with prodigal
# 6. Modify headers

## Here's a use example
## python ~/primate_data_to_IGC.py --indir /dfs/Sharpton_Lab/hammera/IGC/primate_metagenomes/Homo_sapiens/hadza_data/ --outdir /ssd/hammera/IGC/Homo_sapiens/ --host_genome /dfs/Sharpton_Lab/hammera/IGC/host_genomes/Homo_sapiens/GCA_000001405.28_GRCh38.p13_genomic.fna.gz --number_processors 40 --taxa_name Homo_sapiens


import argparse, sys
import sys
import os

parser=argparse.ArgumentParser()

##Read in the necessary arguments
parser.add_argument('--indir', type=str, help='Directory of input files')
parser.add_argument('--outdir', type=str,  help='Directory to write output to')
parser.add_argument('--host_genome', type=str, help='Host taxa genome')
parser.add_argument('--number_processors', type=int, help='Number of processors')
parser.add_argument('--taxa_name', type=str, help='Taxa name, include _ in spaces')
## parse the arguments which are supplied
args=parser.parse_args()

## assign the arguments to distinct variable names
## directory that contains info about read files
indir = args.indir
## writing everything out to this directory
outdir = args.outdir
## host genome file
host_genome = args.host_genome
## number of processors to be used
number_processors = args.number_processors
## host taxa name
taxa_name = args.taxa_name

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(number_processors)

## Kill switch if an argument isn't supplied
#if indir == None or outdir == None or host_genome == None:
#	print("Insufficient number of arguments supplied")
#	sys.exit()

def rsync_data(rsync_outdir, rsync_host_name):
	if os.path.isdir(str("/dfs/Sharpton_Lab/hammera/IGC/primate_metagenomes/" + rsync_host_name + "/")):
		rsync_command = str("rsync -vru " + rsync_outdir + "* /dfs/Sharpton_Lab/hammera/IGC/primate_metagenomes/" + rsync_host_name)
		print("Now rsyncing contents of directory " + rsync_outdir + " to /dfs/Sharpton_Lab/hammera/IGC/primate_metagenomes/" + rsync_host_name)
		os.system(rsync_command)
	return None

def run_cdhit(cdhit_outdir, cdhit_n_procs, cdhit_taxa_name):
	cdhit_dir = str(cdhit_outdir + "cdhit/")
	make_cdhit_dir = str("mkdir " + cdhit_dir)
	os.system(make_cdhit_dir)
	cdhit_command = str("/raid1/home/micro/hammera/bin/cd-hit/cd-hit-est -c 0.95 -G 0 -n 8 -M 0 -aS 0.9 -g 1 -T " + str(cdhit_n_procs) + " -i " + cdhit_outdir + "prodigal/" + cdhit_taxa_name + "_genes_ALL.fna -o " + cdhit_dir + cdhit_taxa_name + "_genes_NR.fa")
	print("Now running CDHIT")
	print(cdhit_command)
	os.system(cdhit_command)
	return None

def run_shotcleaner(shotcleaner_indir, shotcleaner_outdir, shotcleaner_n_procs, bowtie_host_db_name):
	print("NOW EXECUTING SHOTCLEANER FOR HOST GENOME")
	processed_outdir = str(shotcleaner_outdir + "processed/")
	os.system(str("mkdir " + processed_outdir))
	shotcleaner_command = str("perl ~/scripts/run_shotcleaner_single_end.pl --indir=" + shotcleaner_indir + " --outdir=" + processed_outdir + " --nprocs=" + str(shotcleaner_n_procs) + " --db=/ssd/hammera/IGC/bowtie/bowtie_indices/ --dbname=" + bowtie_host_db_name)
	print(shotcleaner_command)
	os.system(shotcleaner_command)
	return None

def get_shotcleaner_clean_file_names_and_megahit(file_outdir, megahit_procs):
	import subprocess
	output = subprocess.check_output(str("ls -d " + file_outdir + "processed/*/fasta_cleaned/*R1_*"), shell=True)
	new_obj = output.split('\n')
	if new_obj[(len(new_obj)-1)] == '':
		new_obj.pop((len(new_obj)-1))
	R1_str = ''
	for i in new_obj:
		if new_obj.index(i) == (len(new_obj) - 1):
			R1_str = str(R1_str + i)
		else:
			R1_str = str(R1_str + i + ',')
	R2_str = R1_str.replace('R1_', 'R2_')
	assembly_dir = str(file_outdir + "assembled/")
	megahit_command = str("/raid1/home/micro/hammera/bin/MEGAHIT-1.2.9-Linux-x86_64-static/bin/megahit --memory 0.9 -t " + str(megahit_procs) + " -1 " + R1_str + " -2 " + R2_str + " -o " + assembly_dir)
	print("NOW RUNNING MEGAHIT")
	print(megahit_command)
	os.system(megahit_command)
	return None


def run_prodigal(prodigal_outdir, prodigal_host_name):
	prodigal_output_directory = str(prodigal_outdir + "prodigal/")
	os.system(str("mkdir " + prodigal_output_directory))
	prodigal_command = str("/raid1/home/micro/hammera/bin/Prodigal-2.6.1/prodigal -q -c -p meta -a " + prodigal_output_directory + "proteins.faa -d " + prodigal_output_directory + "genes.fna -i " + prodigal_outdir + "assembled/final.contigs.fa -o " + prodigal_output_directory + prodigal_host_name + "_sequence_data.log")
	print("NOW RUNNING PRODIGAL")
	print(prodigal_command)
	os.system(prodigal_command)
	return None

def modify_protein_headers(outdir_of_files_to_modify, host_taxa_name):
	ph_outdir = str(outdir_of_files_to_modify + "prodigal/") 
	modify_protein_headers_command = str("perl ~/scripts/modify_protein_headers.pl --type p --in " + ph_outdir + "proteins.faa --out " + ph_outdir + host_taxa_name + "_proteins_ALL.faa" + " --host " + host_taxa_name + " --mapping " + ph_outdir + host_taxa_name + "_map.txt")
	print(modify_protein_headers_command)
	modify_gene_headers_command = str("perl ~/scripts/modify_protein_headers.pl --type p --in " + ph_outdir + "genes.fna --out " + ph_outdir + host_taxa_name + "_genes_ALL.fna" + " --host " + host_taxa_name + " --mapping " + ph_outdir + host_taxa_name + "_gene_map.txt")
	os.system(modify_protein_headers_command)
	os.system(modify_gene_headers_command)
	return None

def build_bowtie_database(host_genome_file, host_name, n_procs):
	print("NOW EXECUTING BOWTIE2-BUILD FOR HOST GENOME:")
	bowtie_command = str("~/bin/bowtie2-2.4.2-sra-linux-x86_64/bowtie2-build --threads "+ str(n_procs) + " " + host_genome_file + " " +  "/ssd/hammera/IGC/bowtie/bowtie_indices/" + host_name)
	print(bowtie_command)
	os.system(bowtie_command)
	return None


def make_ssd_directory(host_scientific_name):
	mkdir_ssd = str("mkdir /ssd/hammera/IGC/" + host_scientific_name + "/")
	print("Making host scientific name directory on SSD")
	os.system(mkdir_ssd)
	return None

#make_ssd_directory(taxa_name)	
build_bowtie_database(host_genome, taxa_name, number_processors)
run_shotcleaner(indir, outdir, number_processors, taxa_name)
#get_shotcleaner_clean_file_names_and_megahit(outdir, number_processors)
#run_prodigal(outdir, taxa_name)
#modify_protein_headers(outdir, taxa_name)
#run_cdhit(outdir, number_processors, taxa_name)
#rsync_data(outdir, taxa_name)



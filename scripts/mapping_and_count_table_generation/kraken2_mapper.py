#!/usr/bin/env python

## This script is just a kraken wrapper takes a directory that contains files you want to map with kraken, the number of processors you want to use
## the kraken2 dtabase, and the location to output all the data

import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join


parser=argparse.ArgumentParser()
## For a test case: python read_to_bam.py --processed_dir /ssd/hammera/IGC/ley_data/xbam/processed/ --out /ssd/hammera/IGC/ley_data/outdir/ --host_IGC /ssd/hammera/IGC/bowtie/Homo_sapiens_IGC_indices/ --number_processors 1 --taxa_name Homo_sapiens

##Read in the necessary arguments
parser.add_argument('--fasta_dir', type=str, help='Directory of fasta files')
parser.add_argument('--number_processors', type=int, help='Number of processors')
parser.add_argument('--kraken2_db', type=str, help='kraken2 db')
parser.add_argument('--out_location', type=str, help='output location')
## parse the arguments which are supplied
args=parser.parse_args()

## directory that contains info about read files
fasta_dir = args.fasta_dir
## number of processors to be used
number_processors = args.number_processors
## kraken2 db
kraken2_db = args.kraken2_db

## output location
out_location = args.out_location

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(number_processors)

def get_file_names(file_indir, pattern_to_match):
        import subprocess
        protein_files = subprocess.check_output(str("ls -d " + file_indir + "*." + pattern_to_match), shell=True)
        protein_list = protein_files.split('\n')
        protein_list.pop()
        return(protein_list)

def get_sample_name(file_name_full):
        file_split = file_name_full.split("/")
        protein_file_name = file_split[-1]
        protein_file_split = protein_file_name.split(".fa.gz")
        some_host_name = str("sample_" + protein_file_split[0])
        return(some_host_name)

def build_bowtie_database(host_genome_file, host_name, n_procs):
        print("NOW EXECUTING BOWTIE2-BUILD FOR HOST GENOME:")
        bowtie_command = str("~/bin/bowtie2-2.4.2-sra-linux-x86_64/bowtie2-build --threads "+ str(n_procs) + " " + host_genome_file + " " +  "/ssd/hammera/IGC/bowtie/bowtie_indices/" + host_name)
        print(bowtie_command)
        os.system(bowtie_command)
	return None

def unleash_the_kraken2(list_of_file_names, your_kraken_db, location_write_to, number_of_threads):
	for single_file in list_of_file_names:
		abbreviated_name = get_sample_name(single_file)
		kraken2_mapping_command = str("~/bin/kraken2_2.0.8/kraken2 --db " + your_kraken_db + " --threads " + str(number_of_threads) + " --report " + location_write_to + abbreviated_name + ".kreport2 --use-mpa-style " + single_file + " > " + location_write_to + abbreviated_name + ".kraken2")
		print(kraken2_mapping_command)
		os.system(kraken2_mapping_command)
	return None



full_list_fastas = get_file_names(fasta_dir, "gz")
unleash_the_kraken2(full_list_fastas, kraken2_db, out_location, number_processors)


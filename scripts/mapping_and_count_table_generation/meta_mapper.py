#!/usr/bin/env python

import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join

## SCRIPT USE: This is a wrapper for some other code I've written which will map a bunch
## of different primate processed reads to some IGC which has been generated
## it requires the number of processors to be specifed, the correct directory structure
## on dfs with a processed file of shotcleanered reads, and a directory containing the cd-hitted
## DNA based IGC for a specific host taxa or set of taxa

parser=argparse.ArgumentParser()

##Read in the necessary arguments
parser.add_argument('--gene_file_directory', type=str, help='Directory of processed files')
parser.add_argument('--number_processors', type=int, help='Number of processors')
## parse the arguments which are supplied
args=parser.parse_args()

## directory that contains info about read files
gene_file_directory = args.gene_file_directory
## number of processors to be used
number_processors = args.number_processors

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(number_processors)

def get_file_names(file_indir, pattern_to_match):
        import subprocess
        protein_files = subprocess.check_output(str("ls -d " + file_indir + "*." + pattern_to_match), shell=True)
        protein_list = protein_files.split('\n')
        protein_list.pop()
        return(protein_list)

def get_host_name(file_name_full):
        file_split = file_name_full.split("/")
        protein_file_name = file_split[-1]
        protein_file_split = protein_file_name.split("_")
        some_host_name = str(protein_file_split[0] + "_" + protein_file_split[1])
        return(some_host_name)

def build_bowtie_database(host_genome_file, host_name, n_procs):
        print("NOW EXECUTING BOWTIE2-BUILD FOR HOST GENOME:")
        bowtie_command = str("~/bin/bowtie2-2.4.2-sra-linux-x86_64/bowtie2-build --threads "+ str(n_procs) + " " + host_genome_file + " " +  "/ssd/hammera/IGC/bowtie/bowtie_indices/" + host_name)
        print(bowtie_command)
        os.system(bowtie_command)
	return None

def rsync_data(rsync_from, rsync_to):
	rsync_command = str("rsync -vru " + rsync_from + "* " + rsync_to)
        print("Now rsyncing contents of directory " + rsync_from + " to " + rsync_to)
        os.system(rsync_command)
        return None

def invoke_python_to_map_reads(IGC_list, n_processors):
	for individual_IGC in IGC_list:
		read_map_host_name = get_host_name(individual_IGC)
		make_host_dir = str("/ssd/hammera/IGC/primates/" + read_map_host_name + "/")
		if (not os.path.isdir(make_host_dir)):
			make_host_directory_command = str("mkdir " + make_host_dir)
			os.system(make_host_directory_command)
		build_bowtie_database(individual_IGC, read_map_host_name, n_processors)
		python_mapping_command =str("python ~/scripts/read_to_bam.py --processed_dir /dfs/Sharpton_Lab/hammera/IGC/primate_metagenomes/" + read_map_host_name + "/processed/" + " --out " + make_host_dir + " --host_IGC /ssd/hammera/IGC/bowtie/bowtie_indices/ --number_processors " + str(n_processors) + " --taxa_name " + read_map_host_name)
		print(python_mapping_command)
		os.system(python_mapping_command)
		clear_bowtie_indices = str("rm -f /ssd/hammera/IGC/bowtie/bowtie_indices/*")
		os.system(clear_bowtie_indices)
		rsync_mapping_directory = str("/dfs/Sharpton_Lab/hammera/IGC/primate_metagenomes/" + read_map_host_name + "/mapped_reads/")
		if (not os.path.isdir(rsync_mapping_directory)):
			make_mapping_directory = str("mkdir " + rsync_mapping_directory)
			os.system(make_mapping_directory)
		rsync_data(make_host_dir, rsync_mapping_directory)
		clear_host_ssd_command = str("rm -f " + make_host_dir + "bowtie_mapped_data/*")
		os.system(clear_host_ssd_command)
	return None

full_list_of_IGC_gene_files = get_file_names(gene_file_directory, "fa")
invoke_python_to_map_reads(full_list_of_IGC_gene_files, number_processors) 




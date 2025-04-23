#!/usr/bin/env python

import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join

## SCRIPT USE: This is a wrapper for some other code I've written which will map a bunch
## of different primate processed reads to some bt database which has been generated
## it requires the number of processors to be specifed, the correct directory structure
## on dfs with a processed file of shotcleanered reads, and a directory containing the cd-hitted
## DNA based IGC for a specific host taxa or set of taxa

parser=argparse.ArgumentParser()
## 


##Read in the necessary arguments
parser.add_argument('--gene_file_directory', type=str, help='Directory of processed files')
parser.add_argument('--out_dir', type=str, help='Directory to write out to')
parser.add_argument('--number_processors', type=int, help='Number of processors')
## parse the arguments which are supplied
args=parser.parse_args()

## directory that contains info about read files
gene_file_directory = args.gene_file_directory
out_dir = args.out_dir
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

def map_to_kegg_database(host_IGC_file, n_procs, write_out_file):
	host_taxa_name = get_host_name(host_IGC_file)
	host_out_file_name = str(write_out_file + host_taxa_name + "_KEGG_mapping.txt")
        diamond_mapping_command = str("~/bin/diamond blastp -q " + host_IGC_file + " -p " + str(n_procs) + " -d /dfs/Sharpton_Lab/hammera/IGC/diamond_kegg/KEGG_db/KEGG_v2019_0.9.24.125.dmnd -o " + host_out_file_name + " -f 6 qseqid sseqid qlen slen length qstart qend sstart send pident gaps evalue bitscore -k 1 &> " + str(write_out_file + host_taxa_name + "_log.txt"))
	print(diamond_mapping_command)
	os.system(diamond_mapping_command)
        return None

def rsync_data(rsync_from, rsync_to):
        rsync_command = str("rsync -vru " + rsync_from + "* " + rsync_to)
        print("Now rsyncing contents of directory " + rsync_from + " to " + rsync_to)
        os.system(rsync_command)
        return None

protein_files_to_map = get_file_names(gene_file_directory, "faa")
for gene_file in protein_files_to_map:
	map_to_kegg_database(gene_file, number_processors, out_dir)


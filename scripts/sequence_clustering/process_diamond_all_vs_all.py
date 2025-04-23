#!/usr/bin/env/python
import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join
import numpy as np
import pandas as pd
parser=argparse.ArgumentParser()

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

## Here's a use example

# python /dfs/Sharpton_Lab/hammera/IGC/homology_analysis/process_txt/process_diamond_all_vs_all.py --diamond_results /dfs/Sharpton_Lab/hammera/IGC/homology_analysis/process_txt/test_process/ --out /dfs/Sharpton_Lab/hammera/IGC/homology_analysis/process_txt/test_process/ --number_processors 3

## The purpose of this script is to turn non-redundant protein sequences from a variety of hosts
## into a set of clusters using the mcl algorithm.

##Read in the necessary arguments
parser.add_argument('--diamond_results', type=str, help='Directory of diamond results')
parser.add_argument('--out', type=str,  help='Directory to write output to')
parser.add_argument('--number_processors', type=int, help='Number of processors')
## parse the arguments which are supplied
args=parser.parse_args()
## assign the arguments to distinct variable names
## directory that contains info about read files
diamond_results = args.diamond_results
## writing everything out to this directory
out = args.out
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

def build_list_of_mcl_edges(diamond_file_directory):
	mcl_file_list = get_file_names(diamond_file_directory, "txt")
	for diamond_file in mcl_file_list:
		for a_chunk in pd.read_csv(diamond_file, chunksize=10000000):
			print(a_chunk.head())
	return None

def add_edges(your_diamond_file, place_to_write):
	search_cutoff = 0.79
        dbsize = 6249504641
        split_file_name = your_diamond_file.split('/')
        file_base_name = (split_file_name[-1])
        temp_list = []
	rsync_file = str("rsync -vu " + your_diamond_file + " " + place_to_write + file_base_name)
	os.system(rsync_file)
	new_file_name = str(place_to_write + file_base_name)
        with open(new_file_name) as difi:
		for line in difi:
			line.rstrip()
                        new_line = line.split()
                        query_coverage = (float(new_line[4])/float(new_line[2]))
                        db_seq_coverage = (float(new_line[4])/float(new_line[3]))
                        adjusted_eval = (dbsize*float(new_line[2]))*(2**((-1)*(float(new_line[12]))))
                        if ((query_coverage > search_cutoff) & (db_seq_coverage > search_cutoff) & (new_line[0] != new_line[1]) & (adjusted_eval < 0.0000000001)):
                        	new_edge = [new_line[0], new_line[1], new_line[9]]
                                temp_list.append(new_edge)
                difi.close()
                output_file_name = str(place_to_write + "mcl_edge_list.txt")
                with open(output_file_name, 'a') as write_out_file:
                        for item in temp_list:
                                write_out_file.write(item[0] + '\t' + item[1] + '\t' + item[2] + '\n')
                write_out_file.close()
		rm_diamond_file = str("rm -f " + new_file_name)
		os.system(rm_diamond_file)
	return None


def get_all_file_names(all_files_location, write_location):
	mcl_file_list = get_file_names(all_files_location, "txt")
	for a_diamond_file in mcl_file_list:
		add_edges(a_diamond_file, write_location)
	return None

get_all_file_names(diamond_results, out)

#build_list_of_edges(diamond_results, out)


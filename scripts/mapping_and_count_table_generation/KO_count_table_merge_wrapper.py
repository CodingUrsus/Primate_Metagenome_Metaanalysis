#!/usr/bin/env python

import sys
import os
import re
import glob
import argparse
import numpy as np
import pandas as pd
from os import listdir
from os.path import isfile, isdir, join

parser=argparse.ArgumentParser()


##Read in the necessary arguments
parser.add_argument('--count_table_directory', type=str, help='Directory of count_tables')
parser.add_argument('--gene_ko_mapping_file_directory', type=str, help='What it says on the box')
parser.add_argument('--out_location', type=str, help='write out to here')
## parse the arguments which are supplied
args=parser.parse_args()

## directory that contains info about read files
count_table_directory = args.count_table_directory
gene_ko_mapping_file_directory = args.gene_ko_mapping_file_directory
out_location = args.out_location
## number of processors to be used

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(1)


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

def build_normalized_KO_table(count_tab, gene_mapping_fi, out_loc):
	KO_table_command = str("python ~/scripts/combine_KO_and_count_table.py --count_table " + count_tab + " --gene_ko_mapping_file " + gene_mapping_fi + " --out_location " + out_loc)
	#print(KO_table_command)
	os.system(KO_table_command)
	return None

count_table_list = get_file_names(count_table_directory, "txt")
mapping_file_list = get_file_names(gene_ko_mapping_file_directory, "txt")

for some_count_table in count_table_list:
	temp_host_name = get_host_name(some_count_table)
	for some_mapping_file in mapping_file_list:
		if temp_host_name in some_mapping_file:
			build_normalized_KO_table(some_count_table, some_mapping_file, out_location)






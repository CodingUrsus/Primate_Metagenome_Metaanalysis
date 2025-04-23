#!/usr/bin/env python


## It's simple, just get the files from the diamond mapping, then feed them into this
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
parser.add_argument('--indir', type=str, help='Directory of input files')
parser.add_argument('--outdir', type=str,  help='Directory to write output to')
## parse the arguments which are supplied
args=parser.parse_args()

## assign the arguments to distinct variable names
## directory that contains info about read files
indir = args.indir
## writing everything out to this directory
outdir = args.outdir

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

def get_file_and_store_homology_data(count_table_to_normalize):
        initial_df = pd.read_csv(count_table_to_normalize, sep='\t', engine='python')
	##print(initial_df.shape)
	subsetted_df = initial_df.iloc[:, [0,9,11]]
	subsetted_df.columns = ["qseqid", "pident", "evalue"]
	quality_evalue_df = subsetted_df[subsetted_df.evalue < 0.001]
	##print(quality_evalue_df.shape)
	identity_dir = []
	for xi in range(21):
		percent_match = (sum(quality_evalue_df.pident > ((xi*100)/20)))
		identity_dir.append(percent_match)	
	return(identity_dir)


homology_file_data = get_file_names(indir, "txt")
host_list = []
perc_identity = []
homology_data = []
for x in homology_file_data:
	some_file = get_file_and_store_homology_data(x)
	for ax in some_file:
		homology_data.append(ax)
	for ix in range(21):
		host_list.append(get_host_name(x))
		perc_identity.append((ix*100)/20)


final_df = pd.DataFrame()
final_df['percent_identity'] = perc_identity
final_df['percent_homologous'] = homology_data
final_df['host'] = host_list

final_df.to_csv(str(outdir + "homology_data.csv"), sep = '\t', index = False)






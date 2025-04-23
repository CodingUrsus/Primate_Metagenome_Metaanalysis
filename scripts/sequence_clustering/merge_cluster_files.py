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

## This script takes the directory of count tables that end in csv from the earlier python script ~/scripts/combine_KO_and_count_table.py which itself takes the results of a mapping of genes to KOs
## Basically it accepts all the KO files for taxa and merges them

##Read in the necessary arguments
parser.add_argument('--count_table_directory', type=str, help='Directory of normalized and cluster annotated count_tables')
parser.add_argument('--out_location', type=str, help='write out to here')
## parse the arguments which are supplied
args=parser.parse_args()

count_table_directory = args.count_table_directory
out_location = args.out_location

os.environ["MKL_NUM_THREADS"] = str(4)

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

count_table_list = get_file_names(count_table_directory, "csv")

df = pd.read_csv(count_table_list[0], sep=',', engine='python')
for df_ in count_table_list[1:]:
	merged_df = pd.read_csv(df_, sep=',', engine='python')
	df = df.merge(merged_df, how='outer', on='cluster')
df.fillna(0, inplace=True)
df.to_csv(str(out_location + "final_cluster_table.csv"))



#!/usr/bin/env python

## example of use
## python create_mcl_cluster_count_table.py --count_table /ssd/hammera/IGC/workshop/cluster_KO_merging/Papio_test/Papio_ursinus_counts.txt --gene_cluster_mapping_file /ssd/hammera/IGC/workshop/cluster_KO_merging/Papio_test/cluster_gene_file.txt --out_location /ssd/hammera/IGC/workshop/cluster_KO_merging/Papio_test/


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
parser.add_argument('--count_table', type=str, help='Directory of count_tables')
parser.add_argument('--gene_cluster_mapping_file', type=str, help='What it says on the box')
parser.add_argument('--out_location', type=str, help='write out to here')
## parse the arguments which are supplied
args=parser.parse_args()

## directory that contains info about read files
count_table = args.count_table
gene_cluster_mapping_file = args.gene_cluster_mapping_file
out_location = args.out_location

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
#os.environ["MKL_NUM_THREADS"] = str(1)


def make_geneID_to_KO_hash(gram_of_hash):
        gene_ID_to_KO_hash = {}
        with open(gram_of_hash, 'r') as genes:
                for line in genes:
                                new_line = (line.split('\t'))
                                gene_ID_to_KO_hash[new_line[0]] = new_line[1].strip()
        return(gene_ID_to_KO_hash)

def get_host_name(file_name_full):
        file_split = file_name_full.split("/")
        protein_file_name = file_split[-1]
        protein_file_split = protein_file_name.split("_")
        some_host_name = str(protein_file_split[0] + "_" + protein_file_split[1])
        return(some_host_name)


def make_sub_dict(cluster_hash_file, your_count_table, out_loc):
	sub_host_name = get_host_name(your_count_table)
	sub_out_file = str(out_loc + sub_host_name + "_cluster_hash.txt")
	grep_command = ('grep "' + sub_host_name + '" ' + cluster_hash_file + ' > ' + sub_out_file)
	if sub_host_name != "Homo_sapiens":
		os.system(grep_command)
		return sub_out_file
	else:
		return cluster_hash_file

def get_file_names(file_indir, pattern_to_match):
        import subprocess
        protein_files = subprocess.check_output(str("ls -d " + file_indir + "*." + pattern_to_match), shell=True)
        protein_list = protein_files.split('\n')
        protein_list.pop()
        return(protein_list)

def tpm_normalization_function(count_table_to_normalize):
        df_to_normalize = pd.read_csv(count_table_to_normalize, sep='\t', engine='python')
        counts_only_df = df_to_normalize.iloc[:,2:]
        normalized_length = (1000/df_to_normalize.length)
        df_1 = (counts_only_df.transpose() * normalized_length)
	normalized_read_depth = (1000000 / df_1.sum(axis=0))
        df_2 = (df_1.transpose() * normalized_read_depth)
        df_2["gene"] = df_to_normalize.contig
        return (df_2)



#test1 = make_sub_dict(gene_cluster_mapping_file, count_table, out_location)
#gene_cluster_hash = make_geneID_to_KO_hash(test1)
count_data_frame = tpm_normalization_function(count_table)
#gene_cluster_dataframe = pd.DataFrame.from_dict(gene_cluster_hash, orient='index')
#cluster_df = gene_cluster_dataframe.reset_index()
#cluster_df.columns = ['gene', 'cluster']
#not_final_df = pd.merge(count_data_frame, cluster_df, how='left', on = ['gene'])
#still_not_final_df = not_final_df.drop(['gene'], axis=1)
#penultimate_df = still_not_final_df.groupby(['cluster']).sum()
#host_name = get_host_name(count_table)
#penultimate_df.to_csv(str(out_location + host_name + "_cluster_count_table.csv"))
#temp_hash_delete = "rm -f " + test1
#os.system(temp_hash_delete)





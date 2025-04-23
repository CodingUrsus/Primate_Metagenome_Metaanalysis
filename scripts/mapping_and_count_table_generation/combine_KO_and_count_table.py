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

## This script was written at night, where there was little concern for efficiency and just piecemeal improvement
## It takes a couple arguments, the first is a count table with contig, length, and the sampleids/counts, the second
## is a ko_mapping file that is formatted in the way that others in the lab outlined in the IGC_methods recommendations
## finally it outputs the merged and normalized KO table to some directory that you specify

## The count table and mapping file need to both start with the host taxa's scienctific name as outlined in the example code below.

## python combine_KO_and_count_table.py --count_table /ssd/hammera/IGC/primates/count_tables/raw_counts/Papio_ursinus_counts.txt --gene_ko_mapping_file /ssd/hammera/IGC/primates/KO_mapping_files/Papio_ursinus_KEGG_mapping.txt --out_location /ssd/hammera/IGC/primates/count_tables/KO_count_table/

##Read in the necessary arguments
parser.add_argument('--count_table', type=str, help='Directory of count_tables')
parser.add_argument('--gene_ko_mapping_file', type=str, help='What it says on the box')
parser.add_argument('--out_location', type=str, help='write out to here')
## parse the arguments which are supplied
args=parser.parse_args()

## directory that contains info about read files
count_table = args.count_table
gene_ko_mapping_file = args.gene_ko_mapping_file
out_location = args.out_location
## number of processors to be used

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(1)


def make_geneID_to_KO_hash(gram_of_hash):
        gene_ID_to_KO_hash = {}
        with open(gram_of_hash, 'r') as genes:
                for line in genes:
                                new_line = (line.split('\t'))
                                gene_ID_to_KO_hash[new_line[0]] = new_line[1]
        return(gene_ID_to_KO_hash)

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

def fpkm_normalization_function(count_table_to_normalize): 
	df_to_normalize = pd.read_csv(count_table_to_normalize, sep='\t', engine='python')
	counts_only_df = df_to_normalize.iloc[:,2:]
	normalized_read_depth = (1000000 / counts_only_df.sum(axis=0))
	normalized_length = (1000/df_to_normalize.length)
	df_1 = (counts_only_df.transpose() * normalized_length)
	df_2 = (df_1.transpose() * normalized_read_depth)
	df_2['contig'] = df_to_normalize.contig
	return (df_2)

count_data_frame = fpkm_normalization_function(count_table)
gene_KO_hash = make_geneID_to_KO_hash("/ssd/hammera/databases/prokaryote_gene_to_KO.dat")
gene_KO_dataframe = pd.DataFrame.from_dict(gene_KO_hash, orient='index')
KO_df = gene_KO_dataframe.reset_index()
KO_df.columns = ['KO_gene', 'KO']
host_gene_mapping_file = make_geneID_to_KO_hash(gene_ko_mapping_file)
host_gene_KO_dataframe = pd.DataFrame.from_dict(host_gene_mapping_file, orient='index')
new_df = host_gene_KO_dataframe.reset_index()
new_df.columns = ['contig', 'KO_gene']
merged_df = new_df.merge(KO_df, how='left', on='KO_gene')
not_final_df = count_data_frame.merge(merged_df, how='left', on='contig')
still_not_final_df = not_final_df.drop(['KO_gene'], axis=1)
before_grouping_df = still_not_final_df[still_not_final_df['KO'] != '']
another_filter = before_grouping_df[before_grouping_df['KO'].notnull()]
penultimate_df = another_filter.groupby(['KO']).sum()
host_name = get_host_name(gene_ko_mapping_file)
penultimate_df.to_csv(str(out_location + host_name + "_KO_table.csv"))



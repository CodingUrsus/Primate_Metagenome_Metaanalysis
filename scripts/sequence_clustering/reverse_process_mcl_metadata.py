#!/usr/bin/env python

import sys
import os
import re
import argparse
import numpy as np
from os import listdir

parser=argparse.ArgumentParser()


## use case: python reverse_process_mcl_metadata.py --cluster_mapping_file /scratch/hammera/IGC/parafit/data/host_parafit_mapping_info.txt --unique_cluster_file /scratch/hammera/IGC/parafit/workshop/testy_boy/unique_clusters.txt --out_location /scratch/hammera/IGC/parafit/workshop/testy_boy/


##Read in the necessary arguments
parser.add_argument('--cluster_mapping_file', type=str, help='File of protein cluster mapping first column is gene, second is cluster')
parser.add_argument('--unique_cluster_file', type=str, help='File of unique cluster names')
parser.add_argument('--out_location', type=str, help='write out to here')
## parse the arguments which are supplied
args=parser.parse_args()

cluster_mapping_file = args.cluster_mapping_file
unique_cluster_file = args.unique_cluster_file
out_location = args.out_location

#os.environ["MKL_NUM_THREADS"] = str(1)

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

def read_in_mapping_file(my_mapping_file):
	nice_lines = [gene.strip() for gene in open(my_mapping_file)]
	return nice_lines

def get_unique_cluster_dict(my_unique_clusters):
	my_cluster_list = [a_line.strip() for a_line in open(my_unique_clusters)]
	cluster_dict = {k: [] for k in my_cluster_list}
	return cluster_dict

def process_the_mapping_file_list(map_list, the_cluster_dict):
	my_counter = 0
	for line in map_list:
		tiny_data = line.split('\t')
		the_cluster_dict[tiny_data[1]].append(tiny_data[0])
		my_counter+=1
		if my_counter%10000==0:
			print(str("processed " + str(my_counter) + " lines"))
	test_1 = the_cluster_dict["cluster_0"]
	dict_list = the_cluster_dict.items()
	return dict_list

mapping_list = read_in_mapping_file(cluster_mapping_file)
cluster_list = get_unique_cluster_dict(unique_cluster_file)
my_cluster_mapping_list = process_the_mapping_file_list(mapping_list, cluster_list)
write_list_out = np.savetxt((out_location + "single_line_cluster_mapping_file.txt"), my_cluster_mapping_list, delimiter="\t", fmt='%s')



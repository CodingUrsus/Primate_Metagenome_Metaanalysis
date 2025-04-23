#!/usr/bin/env python

# this file should actually be used for processing mcxdump output that basically has a file with gene names on each line for each cluster 

from Bio import SeqIO
import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join


parser=argparse.ArgumentParser()


##Read in the necessary arguments
parser.add_argument('--mcxload_outfile', type=str, help='File output from mcxload of gene/protein IDs in each cluster (all on one line)')
parser.add_argument('--out', type=str,  help='Directory to write output to')
## parse the arguments which are supplied
args=parser.parse_args()
mcxload_file = args.mcxload_outfile


## writing everything out to this directory
out = args.out


def create_mcxload_cluster_mapping_file(cluster_file):
	cluster_out_list = []
	my_clust_list = [cluster for cluster in open(cluster_file, "r")]
	for cluster_num in range(0, len(my_clust_list)):
		line = my_clust_list[cluster_num]
		split_line = line.split("\t")
		for gene_name in split_line:
			new_gene_name = gene_name.strip()
			gene_clust_pair = [new_gene_name, cluster_num]
			cluster_out_list.append(gene_clust_pair)
			#if (new_gene_name == "Papio_hamadryas_p_1809781_1" or gene_name == "Papio_cynocephalus_p_1755632_3"):
			#	print(str(cluster_num))
	return cluster_out_list

def write_out(cluster_list, out_file_location):
	out_file_name = (out_file_location + "cluster_gene_file.txt")
	outF = open(out_file_name, "w")
	for line in cluster_list:
  # write line to output file
		line_to_write = (line[0] + "\t" + "cluster_" + str(line[1]))
  		outF.write(line_to_write)
		outF.write('\n')
	outF.close()
	return None

mcxload_cluster_list = create_mcxload_cluster_mapping_file(mcxload_file)
write_out(mcxload_cluster_list, out)

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
parser.add_argument('--gene_cluster_file', type=str, help='File mapping genes to clusters')
parser.add_argument('--human_mapping_file', type=str, help='File of named human genes to map')
parser.add_argument('--out', type=str,  help='Directory to write output to')
## parse the arguments which are supplied
args=parser.parse_args()
gene_cluster_file = args.gene_cluster_file
human_mapping_file = args.human_mapping_file

## writing everything out to this directory
out = args.out

def get_host_name(file_name_full):
        name_split = file_name_full.split("_")
        some_host_name = str(name_split[0] + "_" + name_split[1])
        return(some_host_name)


def make_geneID_to_KO_hash(geneID_to_KO_data):
        gene_ID_to_KO_hash = {}
        with open(geneID_to_KO_data, 'r') as genes:
                for line in genes:
                                new_line = (line.split('\t'))
                                gene_ID_to_KO_hash[new_line[0]] = new_line[1].strip()
        return(gene_ID_to_KO_hash)

def parse_gene_cluster_file(my_gene_file, my_human_dict):
	my_named_genes = [z_gene.strip() for z_gene in open(my_gene_file, "r")]
	ordered_genes_to_print = []
	counter = 0
	for gene_in_question in my_named_genes:
		gene_in_question.strip()
		if my_human_dict.has_key(gene_in_question):
			ordered_genes_to_print.append(my_human_dict[gene_in_question])
			counter +=1
			if counter < 100:
				print(my_human_dict[gene_in_question])
		else:
			ordered_genes_to_print.append(gene_in_question)
	return ordered_genes_to_print

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
	out_file_name = (out_file_location + "all_gene_names_correct_list.txt")
	outF = open(out_file_name, "w")
	for line in cluster_list:
  # write line to output file
  		outF.write(line)
		outF.write('\n')
	outF.close()
	return None

human_dict = make_geneID_to_KO_hash(human_mapping_file)
dict_items = human_dict.items()

first_three = list(dict_items)[:10]
print(first_three)

final_gene_list = parse_gene_cluster_file(gene_cluster_file, human_dict)

write_out(final_gene_list, out) 


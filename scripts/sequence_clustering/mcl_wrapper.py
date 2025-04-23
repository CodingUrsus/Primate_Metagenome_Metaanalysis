#!/usr/bin/env python

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
parser.add_argument('--KO_mapping_file_dir', type=str, help='Directory of KO-protein mapping')
parser.add_argument('--protein_file_dir', type=str, help='Directory of IGC protein files')
parser.add_argument('--out', type=str,  help='Directory to write output to')
## parse the arguments which are supplied
args=parser.parse_args()

KO_mapping_file_dir = args.KO_mapping_file_dir
protein_file_dir = args.protein_file_dir

## writing everything out to this directory
out = args.out

def get_gene_names_from_KO_mapping_file(KO_file):
	KO_name_list = []
	with open(KO_file) as KO_first_line:
		for row in KO_first_line:
        		KO_name_list.append(row.split()[0])
	KO_first_line.close()
	print(str(sys.getsizeof(KO_name_list)))
	return(KO_name_list)

def write_list_to_out_file(your_list, your_out_file):
	textfile = open(your_out_file, "w")
	for element in your_list:
    		textfile.write(element + "\n")
	textfile.close()
	return None

def get_file_names(file_indir, pattern_to_match):
        import subprocess
        protein_files = subprocess.check_output(str("ls -d " + file_indir + "*" + pattern_to_match), shell=True)
        protein_list = protein_files.split('\n')
        protein_list.pop()
        return(protein_list)



def get_host_name(a_named_file):
	first_split = a_named_file.split('/')[-1]
        second_split = first_split.split('_')
        host_name = (second_split[0] + "_" + second_split[1])
	return host_name

def find_matching_protein_file(some_file_name, list_of_proteins):
	first_split = some_file_name.split('/')[-1]
	second_split = first_split.split('_')
	host_name = (second_split[0] + "_" + second_split[1])
	for an_element in list_of_proteins:
		if host_name in an_element:
			print(an_element)
			return an_element
	return None

## thsi function takes a ko mapping file dir with gene names in the first column, then a direct with protein
## files to subset
def make_big_list_of_gene_names(KO_file_dir, protein_file_direct, out_file):
	all_KO_mapping_files = get_file_names(KO_file_dir, "mapping.txt")
	all_protein_files = get_file_names(protein_file_direct, "faa")
	write_out = str(out_file + "all_mcl_proteins.faa")
	for a_KO_file in all_KO_mapping_files:
		host_name = get_host_name(a_KO_file)
		list_of_names = get_gene_names_from_KO_mapping_file(a_KO_file)
		host_out_file = str(out_file + host_name + "_sub.txt")
		write_my_list = write_list_to_out_file(list_of_names, host_out_file)
		protein_match = find_matching_protein_file(a_KO_file, all_protein_files)
		out_file_name = str(out_file + host_name + "_mcl_protein_subset.faa")
		seqtk_command = str("seqtk subseq " + protein_match + " " + host_out_file + " > " + out_file_name)
		delete_host_list = str("rm -f " + host_out_file)
		os.system(seqtk_command)
		os.system(delete_host_list)
	return None



## first read in file with ids
def read_file_ids_into_list(list_of_genes):
        with open(list_of_genes) as my_genes:
                gene_names = [line.strip() for line in my_genes]
                return(gene_names)

def process_it_all(my_gene_list, gene_fasta_file):
        seqs_to_return = []
        for seq_rec in SeqIO.parse(gene_fasta_file, "fasta"):
                if (seq_rec.id in my_gene_list):
                        seqs_to_return.append(seq_rec)
        return(seqs_to_return)



make_big_list_of_gene_names(KO_mapping_file_dir, protein_file_dir, out)

#make_big_list_of_gene_names(KO_mapping_file_dir)
#get_gene_names_from_KO_mapping_file(KO_mapping_file, out)
#genes_to_check = (read_file_ids_into_list(gene_names))
#subsetted_seqs = process_it_all(genes_to_check, gene_subset_file)
#SeqIO.write(subsetted_seqs, out, "fasta")







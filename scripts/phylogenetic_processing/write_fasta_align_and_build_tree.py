#!/usr/bin/env python


## use case: python write_fasta_align_and_build_tree.py --file_of_clusters /scratch/hammera/IGC/parafit/data/cluster_processing_data/clusters_of_interest.txt --gene_cluster_info_file /scratch/hammera/IGC/parafit/data/cluster_processing_data/cluster_gene_mapping_file.txt --master_protein_file /scratch/hammera/IGC/parafit/data/host_protein_sets/final_mcl_protein_set.faa --out /scratch/hammera/IGC/parafit/results/

from Bio import SeqIO
import sys
import os
import re
import argparse
import pandas as pd
from os import listdir
from os.path import isfile, isdir, join

parser=argparse.ArgumentParser()

##Read in the necessary arguments
parser.add_argument('--file_of_clusters', type=str, help='File of clusters to build trees for')
parser.add_argument('--gene_cluster_info_file', type=str, help='File of cluster number, followed by cluster members')
parser.add_argument('--master_protein_file', type=str, help="File of all proteins you\'ll access")
parser.add_argument('--out', type=str,  help='Directory to write output to')
## parse the arguments which are supplied
args=parser.parse_args()
file_of_clusters = args.file_of_clusters
gene_cluster_info_file = args.gene_cluster_info_file
master_protein_file = args.master_protein_file
## writing everything out to this directory
out = args.out

## get unique cluster values first
## filter gene_cluster_info_file
## seqtk subseq into cluster_file


def get_host_name(file_name_full):
        name_split = file_name_full.split("_")
        some_host_name = str(name_split[0] + "_" + name_split[1])
        return(some_host_name)

def get_protein_list(gene_names_list, output_dir):
	write_file_name = str(output_dir + "seqtk_gene_names_file.txt")
	write_genes = open(write_file_name, "w")
	for i in gene_names_list:
		write_genes.write(i)
		write_genes.write('\n')
	write_genes.close()
	return write_file_name
	
def seqtk_subseq(subset_file, main_gene_file, out_loca):
	seqtk_command = str("seqtk subseq " + main_gene_file + " " + subset_file + " > " + out_loca + "all_proteins_for_alignment_script.fasta")
	os.system(seqtk_command)
	return (str(out_loca + "all_proteins_for_alignment_script.fasta"))

def align_with_muscle(my_fastas, my_out_loc, clusternumber):
	muscle_exe = "/local/cluster/bin/muscle3.8.31_i86linux64 -quiet"
	cline_please = str(muscle_exe + " -in " + my_fastas + " -out " + my_out_loc + clusternumber + ".aln")
	print(cline_please)
	os.system(cline_please)
	delete_fasta = str("rm -f " + my_fastas)
	os.system(delete_fasta)
	return (str(my_out_loc + clusternumber + ".aln"))

def build_a_fast_tree(alignment_fil, out_loca, clusty_num):
	build_a_tree_command = str("/local/cluster/bin/FastTree -quiet -fastest " + alignment_fil + " > " + out_loca + clusty_num + ".nwk")
	print(build_a_tree_command)
	os.system(build_a_tree_command)
	delete_alignment = str("rm -f " + alignment_fil)
	os.system(delete_alignment)
	return str(out_loca + clusty_num + ".nwk")

def make_dictionary_from_protein_seqs(file_of_protein_seqs):
        protein_hash = {}
	counter = 0
        for protein in SeqIO.parse(file_of_protein_seqs, "fasta"):
                protein_hash[protein.id] = str(protein.seq)
		counter +=1
		if ((counter % 100000) ==0):
			print("Processed " + str(counter) + " sequences")
        return protein_hash

def make_dictionary_for_clusters(cluster_gene_file):
	cluster_dictionary = {}
	my_clust_tracker = 0
	write_clusters = open(cluster_gene_file, "r")
        for i in write_clusters:
		stripped_i = i.strip('\n')
		split_i = stripped_i.split('\t')
		cluster_dictionary[split_i[0]]=split_i[1:]
		my_clust_tracker+=1
		if ((my_clust_tracker % 200000) == 0):
			print("processed " + str(my_clust_tracker) + " clusters")
        write_clusters.close()
#	print(cluster_dictionary["cluster_49981"])
	return(cluster_dictionary)

def make_smaller_protein_sequence_dictionary(cluster_to_gene_dict, all_proteins_file, clusts_of_interest, some_output_location):
	all_protein_names = []
	for single_clust in clusts_of_interest:
		a_clust = single_clust.strip('\n')
		clust_members = cluster_to_gene_dict[a_clust]
		for single_protein_name in clust_members:
			all_protein_names.append(single_protein_name)
	write_file_for_seqtk = get_protein_list(all_protein_names, some_output_location)
	all_proteins_file = seqtk_subseq(write_file_for_seqtk, all_proteins_file, some_output_location)
	my_protein_romance = make_dictionary_from_protein_seqs(all_proteins_file)
	remove_temporary_protein_name_list = str("rm -f " + write_file_for_seqtk)
	os.system(remove_temporary_protein_name_list)
	return my_protein_romance

def make_protein_file_for_alignment(single_cluster, clusters_to_gene_for_alignment_dict, alignment_protein_dict, place_to_write_alignment):
		members = clusters_to_gene_for_alignment_dict[single_cluster]
		the_fasta_file_name = str(place_to_write_alignment + single_cluster + ".fasta")
		write_protein_fasta = open(the_fasta_file_name, "w")
		for a_member in members:
			write_protein_fasta.write(">" + a_member + "\n")
			write_protein_fasta.write(alignment_protein_dict[a_member])
			write_protein_fasta.write('\n')
		write_protein_fasta.close()
		return (the_fasta_file_name)

list_of_clusters = [one_cluster.rstrip('\n') for one_cluster in open(file_of_clusters, "r")]
clust_dict = make_dictionary_for_clusters(gene_cluster_info_file)
tailored_protein_dict = make_smaller_protein_sequence_dictionary(clust_dict, master_protein_file, list_of_clusters, out)
if not os.path.exists(str(out + "trees/")):
	os.system(str("mkdir " + out + "trees/"))
if not os.path.exists(str(out + "alignments/")):
        os.system(str("mkdir " + out + "alignments/"))
if not os.path.exists(str(out + "fastas/")):
        os.system(str("mkdir " + out + "fastas/"))
alignments_directory = str(out+"alignments/")
trees_directory = str(out+"trees/")
fasta_directory = str(out+"fastas/")
for onecluster in list_of_clusters:
	the_cluster_fasta = make_protein_file_for_alignment(onecluster, clust_dict, tailored_protein_dict, fasta_directory)
	
	## these were commented out to make alignment files to map with BLAST
	#the_cluster_alignment = align_with_muscle(the_cluster_fasta, alignments_directory, onecluster)
	#the_cluster_tree = build_a_fast_tree(the_cluster_alignment, trees_directory, onecluster)




#!/usr/bin/env/python

import sys
from Bio import SeqIO

## The purpose of this script is to create an alignment of protein sequences from each cluster
## so that we can test hypotheses of codiversification of protein families with host taxa

all_proteins  = sys.argv[1]
file_of_cluster_headers = sys.argv[2]

## Create a hash of all the protein sequences
## in the future consider cleaning this up by just storing a pre-made
## hash of all the protein sequences. It would probably be a lot faster that way

def hash_of_protein_seqs (file_of_protein_seqs):
	protein_hash = {}
	for protein in SeqIO.parse(file_of_protein_seqs, "fasta"):
		protein_hash[protein.id] = str(protein.seq)
	return protein_hash

try_this = hash_of_protein_seqs(all_proteins)

## Underdeveloped so far, but this takes in the protein hash and the list of clusters which
## contain information about the proteins in the cluster. Using this information, 

def make_cluster_fasta (protein_hash, list_of_clusters):
	clust_num = 0
	with open(list_of_clusters, 'r') as clusters:
		for line in clusters:
			clust_num+=1
			cluster_proteins = line.split()
			if ((len(cluster_proteins) > 4) and (len(cluster_proteins) < 100)):
				new_file_name = "/ssd/hammera/IGC/parafit/alignments/cluster" + str(clust_num) + ".fasta"
				with open(new_file_name, "a") as fasta_file:
					for i in cluster_proteins:
						if i in protein_hash:
							fasta_file.write((">" + i) + "\n" + protein_hash[i] + "\n")
				fasta_file.close()

some_func = make_cluster_fasta(try_this, file_of_cluster_headers)
















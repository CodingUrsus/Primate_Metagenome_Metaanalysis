#!/usr/bin/env/python

import sys
import os
import re
import glob


## This script requires the location of the .aln (protein alignment) files, and the location that the
## parasite-host matrix should be directed to. With this information it will create
## a directory called h_p_matrices where the cluster host-parasite/protein matrices
## are stored.

## The structure of the matrices has the parasite/protein as the columns and
## the host as the row.


location_of_aln_files  = sys.argv[1]
penultimate_directory_for_matrix_storage = sys.argv[2]


def make_a_directory (path_to_directory):
        os.chdir(str(path_to_directory))
	new_directory = str(path_to_directory) + "h_p_matrices/"	
	if not os.path.exists(new_directory):
		os.mkdir(new_directory)

def build_matrix(protein_ids, host_taxa):
	import numpy as np
	import pprint
	import pandas as pd
	blank_df = (np.zeros(dtype=int,shape=(len(host_taxa),len(protein_ids))))
	for i in range(len(host_taxa)):
		for j in range(len(protein_ids)):
			if host_taxa[i] == (protein_ids[j][0:4]).lower():
				blank_df[i,j] = 1
			else:
				blank_df[i,j] = 0
	complete_df = pd.DataFrame(blank_df)
	column_name_dict = dict(zip(complete_df.columns.tolist(), protein_ids))
	row_name_dict = dict(zip(complete_df.index.tolist(), host_taxa))
	finished_df = complete_df.rename(columns=column_name_dict, index=row_name_dict)
	return(finished_df)


def extract_protein_and_taxa (path_to_aln_files, parent_directory):
	os.chdir(str(path_to_aln_files))
	for alignment_file in glob.glob("*.aln"):
		with open(alignment_file, "r") as af:
			vector_of_protein_names = []
			vector_of_host_taxa = []
			for line in af:
				if line[0]=='>':
					vector_of_protein_names.append(line.strip('>').strip('\n'))
					vector_of_host_taxa.append(line[1:5].lower())
		af.close()
		host_taxa = list(set(vector_of_host_taxa))
		taxa_protein_matrix = build_matrix(vector_of_protein_names, host_taxa)
		taxa_protein_matrix.to_csv(str(path_to_directory) + "h_p_matrices/" + alignment_file, header=True, index=True, sep='\t', mode='a')
		
		
		
create_directory = make_a_directory(penultimate_directory_for_matrix_storage)
creating_matrices = extract_protein_and_taxa(location_of_aln_files, penultimate_directory_for_matrix_storage)




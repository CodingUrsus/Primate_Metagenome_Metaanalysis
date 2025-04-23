#!/usr/bin/python

## This script takes three arguments, one which specifies geneIDs which have been mapped
## using diamond to the kegg prokaryote protein database, then another file which contains KO information that specifies
## which KOs are mapped to specific geneIDs, and finally an argument that specifies the output directory

## Be careful that the information in your diamond_kegg_mapping file is appropriate for this script, or modify
## as needed.

import sys
import os
import re
import glob

diamond_kegg_mapping_data = sys.argv[1]
geneID_to_KO_mapping_data = sys.argv[2]
output_directory = sys.argv[3]

def make_geneID_to_KO_hash(geneID_to_KO_data):
	gene_ID_to_KO_hash = {}
	with open(geneID_to_KO_data, 'r') as genes:
                for line in genes:
				new_line = (line.split('\t'))
                        	gene_ID_to_KO_hash[new_line[0]] = line
	return(gene_ID_to_KO_hash)


def write_geneID_KO_table_out(geneID_KO_hash, diamond_kegg_data):
	f = open(diamond_kegg_data, 'r')
	with open((str(output_directory + "gene_KO_mapping_file.txt")), 'w') as write_out:
		for k in f:
			temp_val = k.split()[1]
			if (temp_val in geneID_KO_hash.keys()):
				print(geneID_KO_hash[temp_val])
				write_out.write(geneID_KO_hash[temp_val])
			else:
				print(temp_val)
				write_out.write(temp_val + "\n")

geneID_KO_dict = (make_geneID_to_KO_hash(geneID_to_KO_mapping_data))
write_geneID_KO_table_out(geneID_KO_dict, diamond_kegg_mapping_data)



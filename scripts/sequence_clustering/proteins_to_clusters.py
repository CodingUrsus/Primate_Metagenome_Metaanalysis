#!/usr/bin/env/python
import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join


parser=argparse.ArgumentParser()


## Here's a use example
# python /ssd/hammera/IGC/primates/clust_test/seqs/proteins_to_clusters.py --protein_fastas /ssd/hammera/IGC/primates/clust_test/seqs/ --db_directory /ssd/hammera/IGC/bowtie/bowtie_indices/ --out /ssd/hammera/IGC/primates/clust_test/diamond_mapping/ --number_processors 1


## The purpose of this script is to turn non-redundant protein sequences from a variety of hosts
## into a set of clusters using the mcl algorithm.

##Read in the necessary arguments
parser.add_argument('--protein_fastas', type=str, help='Directory of protein_fastas')
parser.add_argument('--db_directory', type=str, help='Directory to write db files to')
parser.add_argument('--out', type=str,  help='Directory to write output to')
parser.add_argument('--number_processors', type=int, help='Number of processors')
## parse the arguments which are supplied
args=parser.parse_args()
## assign the arguments to distinct variable names
## directory that contains info about read files
protein_fastas = args.protein_fastas
db_directory = args.db_directory
## writing everything out to this directory
out = args.out
## number of processors to be used
number_processors = args.number_processors

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(number_processors)

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

def build_and_map_all_v_all(numb_procs, db_out, write_out, dir_of_fastas):
	all_the_fastas = get_file_names(dir_of_fastas, "faa")
	for a_fasta in all_the_fastas:
		new_diamond_db = build_diamond_db(numb_procs, db_out, a_fasta)
		for fasta_search in all_the_fastas:
			db_host_name = get_host_name(new_diamond_db)
			query_host_name = get_host_name(fasta_search)
			diamond_search_command = str("~/bin/diamond blastp -p " + str(numb_procs) + " -q " + fasta_search + " -d " + new_diamond_db + " -o " + write_out + query_host_name + "_against_" + db_host_name + ".txt" + " -f 6 qseqid sseqid qlen slen length qstart qend sstart send pident gaps evalue bitscore -k 100")
			print(diamond_search_command)
			os.system(diamond_search_command)
		remove_db = str("rm -f " + new_diamond_db)
		os.system(remove_db)
	return None


def build_diamond_db(number_of_processors, db_out_dir, a_protein_fasta):
	some_host_name = get_host_name(a_protein_fasta)
	make_diamond_db_command = str("~/bin/diamond makedb --in " + a_protein_fasta + " -p " + str(number_of_processors) + " -d " + db_out_dir + some_host_name + "_0.9.24")
	#print(make_diamond_db_command)
	new_fasta_db_name = str(db_out_dir + some_host_name + "_0.9.24.dmnd")
	os.system(make_diamond_db_command)
	return (new_fasta_db_name)


build_and_map_all_v_all(number_processors, db_directory, out, protein_fastas)


build_diamond_db(40, "/scratch/hammera


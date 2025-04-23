#!/usr/bin/env python

import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join


parser=argparse.ArgumentParser()


##Read in the necessary arguments
parser.add_argument('--input_directory', type=str, help='Directory of IGC protein files')
parser.add_argument('--out', type=str,  help='Directory to write output to')
parser.add_argument('--number_processors', type=int, help='Number of processors')
## parse the arguments which are supplied
args=parser.parse_args()


input_directory = args.input_directory
## writing everything out to this directory
out = args.out
## number of processors to be used
number_processors = args.number_processors

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(number_processors)


def get_file_names(file_indir):
	import subprocess
	protein_files = subprocess.check_output(str("ls -d " + file_indir + "*.faa"), shell=True)
	protein_list = protein_files.split('\n')
	protein_list.pop()
	return(protein_list)

def run_cdhit(cdhit_outdir, cdhit_n_procs, cdhit_files):
        cdhit_dir = str(cdhit_outdir + "cdhit/")
	if (not os.path.isdir(cdhit_dir)):
        	make_cdhit_dir = str("mkdir " + cdhit_dir)
        	os.system(make_cdhit_dir)
	for protein_file_name in cdhit_files:
		file_name_split = protein_file_name.split("/")
		protein_file = file_name_split[-1]
		protein_name_split = protein_file.split("_")
		host_name = str(protein_name_split[0] + "_" + protein_name_split[1])
        	cdhit_command = str("/raid1/home/micro/hammera/bin/cd-hit/cd-hit -c 0.90 -G 0 -n 5 -M 0 -aS 0.9 -g 1 -T " + str(cdhit_n_procs) + " -i " + protein_file_name + " -o " + cdhit_dir + host_name + "_proteins_NR.faa")
		os.system(cdhit_command)
		print(cdhit_command)
        return None


protein_names = get_file_names(input_directory)
run_cdhit(out, number_processors, protein_names)



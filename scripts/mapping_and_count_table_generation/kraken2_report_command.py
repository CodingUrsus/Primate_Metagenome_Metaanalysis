#!/usr/bin/env python

## This script is just a kraken wrapper takes a directory that contains files you want to map with kraken, the number of processors you want to use
## the kraken2 dtabase, and the location to output all the data

import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join


parser=argparse.ArgumentParser()
## For a test case: python read_to_bam.py --processed_dir /ssd/hammera/IGC/ley_data/xbam/processed/ --out /ssd/hammera/IGC/ley_data/outdir/ --host_IGC /ssd/hammera/IGC/bowtie/Homo_sapiens_IGC_indices/ --number_processors 1 --taxa_name Homo_sapiens

##Read in the necessary arguments
parser.add_argument('--kreport_dir', type=str, help='Directory of report files')
parser.add_argument('--out_name', type=str, help='output name')
## parse the arguments which are supplied
args=parser.parse_args()

## directory that contains info about read files
kreport_dir = args.kreport_dir

## output location
out_name = args.out_name

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(1)

def get_file_names(file_indir, pattern_to_match):
        import subprocess
        protein_files = subprocess.check_output(str("ls -d " + file_indir + "*." + pattern_to_match), shell=True)
        protein_list = protein_files.split('\n')
        protein_list.pop()
        return(protein_list)

def build_command(list_of_files, output_file):
        some_string = 'python ~/bin/krakentools/KrakenTools-master/combine_mpa.py --no-intermediate-ranks -i '
	for i in list_of_files:
		some_string = str(some_string + i + ' ')
	some_string = str(some_string + "-o " + output_file)
	print(some_string)
	return None

full_list_fastas = get_file_names(kreport_dir, "kreport2")
build_command(full_list_fastas, out_name)





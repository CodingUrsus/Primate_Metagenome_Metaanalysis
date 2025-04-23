#!/usr/bin/env python

# Downloaded SRA filenames don't play nicely with shotcleaner, so this script modifies the file name of paired end reads

## Example of how this script might be used
## python change_SRA_file_names.py --file_dir /ssd/hammera/IGC/ley_data/Canis_aureus/ --host_name hostname


import argparse, sys
import sys
import os

parser=argparse.ArgumentParser()

##Read in the necessary arguments
parser.add_argument('--file_dir', type=str, help='Directory of files')
parser.add_argument('--host_name', type=str, help='Host taxa name')
## parse the arguments which are supplied
args=parser.parse_args()

## assign the arguments to distinct variable names
## directory that contains info about read files
file_dir = args.file_dir
host_name = args.host_name

def modify_file_names(file_directory, host_taxa_name):	
	import subprocess
        file_names = subprocess.check_output(str("ls -d " + file_directory + "*_1.fastq.gz*"), shell=True)
	file_list = file_names.split('\n')
	if file_list[len(file_list) - 1] == '':
		file_list.pop()
	counter = 1
	for i in file_list:
		R2_replace = str(i.replace("_1.fastq.gz", "_2.fastq.gz"))
		split_name = i.split('_1.')
		sample_num = str(counter)
		filled_sample = sample_num.zfill(3)
		renamed_file = (str(str(split_name[0]) + "-s" + filled_sample + "-" + host_taxa_name + "_R1_001.fastq.gz"))
		renamed_reverse_file = (str(str(split_name[0]) + "-s" + filled_sample + "-" + host_taxa_name + "_R2_001.fastq.gz"))
		os.system("mv " + str(i) + " " + renamed_file)
                os.system("mv " + R2_replace + " " + renamed_reverse_file)
		counter+=1
	return None

modify_file_names(file_dir, host_name)



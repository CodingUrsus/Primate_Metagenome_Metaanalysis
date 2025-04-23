#!/usr/bin/env/python

import sys
import os
import re
import glob
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
## This script takes an argument for the file to translate, and the second argument
## specifies the directory to write the file to

## Hella slow, if you need it to be fast then multithread it
import argparse, sys
import sys
import os

parser=argparse.ArgumentParser()

##Read in the necessary arguments
parser.add_argument('--infile', type=str, help='input file')
parser.add_argument('--outdir', type=str,  help='Directory to write output to')
## parse the arguments which are supplied
args=parser.parse_args()


## Use example
## python ~/scripts/translate_fasta.py --infile /ssd/hammera/IGC/primate_data/primate_genes/ --outdir /ssd/hammera/IGC/primate_data/primate_proteins/

## assign the arguments to distinct variable names
## directory that contains info about read files
infile = args.infile
## writing everything out to this directory
outdir = args.outdir

import subprocess
files_list = subprocess.check_output(str("ls -d " + infile + "*.fa"), shell=True)
file_list = files_list.split('\n')
file_list.pop()

def translate_function(output_directory, input_file):
	input_file_split_slash = input_file.split("/")
	input_file_name = input_file_split_slash[-1]
	input_file_split = input_file_name.split("_")
	host_taxa_name = str(input_file_split[0] + "_" + input_file_split[1])
	input_file_str = str(input_file)
	out_file_and_directory = str(output_directory + host_taxa_name + "_" + 'translated_NR.faa')
	with open(out_file_and_directory, 'w') as fastaout:
  		for record in SeqIO.parse(input_file_str, 'fasta'):
      			SeqIO.write(SeqRecord(seq=record.seq.translate(table="Bacterial"), id=record.id, description=''), fastaout, 'fasta')
	return None

for gene_fasta_file in file_list:
	translate_function(outdir, gene_fasta_file)
	print(gene_fasta_file)

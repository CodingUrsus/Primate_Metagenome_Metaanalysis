#!/usr/bin/env/python
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
parser.add_argument('--processed_dir', type=str, help='Directory of processed files')
parser.add_argument('--out', type=str,  help='Directory to write output to')
parser.add_argument('--host_IGC', type=str, help='Taxa IGC')
parser.add_argument('--number_processors', type=int, help='Number of processors')
parser.add_argument('--taxa_name', type=str, help='Taxa name, include _ in spaces')
## parse the arguments which are supplied
args=parser.parse_args()

## assign the arguments to distinct variable names
## directory that contains info about read files
processed_dir = args.processed_dir
## writing everything out to this directory
out = args.out
## host genome file
host_IGC = args.host_IGC
## number of processors to be used
number_processors = args.number_processors
## host taxa name
taxa_name = args.taxa_name

## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(number_processors)


def map_reads_with_bowtie(number_of_processors, host_IGC, processed_directory, out_dir, bt_host_name):
	import subprocess
        output = subprocess.check_output(str("ls -d " + processed_directory + "*.fna"), shell=True)
        new_obj = output.split('\n')
        if new_obj[(len(new_obj)-1)] == '':
                new_obj.pop((len(new_obj)-1))
	for reads_file in new_obj:
		reads_file_split = reads_file.split("/")
		simple_name = reads_file_split[-1]
		bowtie_mapping_command = ("bowtie2 -f " + "-k 1 " + "--met-file " + str(out_dir + simple_name + ".txt") + " --threads " + str(number_of_processors) + " -x " + str(host_IGC + bt_host_name) + " -U " + reads_file + " -S " + str(out_dir + simple_name + ".sam") + str(" &> " + out_dir + simple_name + ".log"))
		#print(bowtie_mapping_command)
		os.system(bowtie_mapping_command)
	return None

def return_abbreviated_sample_name(sample_str, split_pattern, split_location):
	split_sample_name = sample_str.split(split_pattern)
	abbrev_sample_name = split_sample_name[split_location]
	return(abbrev_sample_name)

def sam_to_bam(sb_number_of_processors, sb_bowtie_dir):
	import subprocess
	sam_files = subprocess.check_output(str("ls -d " + sb_bowtie_dir + "*.sam"), shell=True)
	sam_list = sam_files.split('\n')
	sam_list.pop()
	for sam_file in sam_list:
		sam_file_abbrev_name = return_abbreviated_sample_name(sam_file, ".f", 0)
		convert_sam_to_bam = str("samtools view -bt --write-index -@ " + str(sb_number_of_processors) + " " + sam_file + " -o " + sam_file_abbrev_name + ".bam")
		#print(convert_sam_to_bam)
		os.system(convert_sam_to_bam)
		delete_sam_file = str("rm -f " + sam_file)
		os.system(delete_sam_file)
	return None

def sort_and_index(si_bowtie_dir, si_numb_procs):
	import subprocess
        bam_files = subprocess.check_output(str("ls -d " + si_bowtie_dir + "*.bam"), shell=True)
	bam_list = bam_files.split('\n')
	bam_list.pop()
	for bam_file in bam_list:
		sorted_bam_name = bam_file.replace('.bam', '_sorted.bam')
		samtools_sort = str("samtools sort -@ " + str(si_numb_procs) + " " + bam_file + " -o " + bam_file.replace('.bam', '_sorted.bam'))
		samtools_index = str("samtools index -@ " + str(si_numb_procs) + " " + sorted_bam_name)
		os.system(samtools_sort)
		os.system(samtools_index)
	return None

def get_mapping_stats(mapping_procs, mapping_file_location):
	import subprocess
        sorted_bam_files = subprocess.check_output(str("ls -d " + mapping_file_location + "*_sorted.bam"), shell=True)
        sorted_bam_list = sorted_bam_files.split('\n')
        sorted_bam_list.pop()
	for sorted_indexed_bam_file in sorted_bam_list:
		short_name = sorted_indexed_bam_file.replace('_sorted.bam', '')
		get_idxstats = str("samtools idxstats -@ " + str(mapping_procs) + " " + sorted_indexed_bam_file + " > " + short_name + "_idx_stats.txt")
		#print(get_idxstats)
		os.system(get_idxstats)
	return None

def get_mapping_stats_for_all(directory_of_idx_stats, stats_host_name):
	get_stats = str("python /raid1/home/micro/hammera/scripts/get_count_table.py " + directory_of_idx_stats + "*idx_stats.txt" + " > " + directory_of_idx_stats + stats_host_name + "_counts.txt")
	print(get_stats)
	os.system(get_stats)
	return None



bowtie_mapped_directory = str(out + "bowtie_mapped_data/")
if (not os.path.isdir(bowtie_mapped_directory)):
	make_bowtie_mapped_directory = str("mkdir " + bowtie_mapped_directory)
	os.system(make_bowtie_mapped_directory)

map_reads_with_bowtie(number_processors, host_IGC, processed_dir, bowtie_mapped_directory, taxa_name)
sam_to_bam(number_processors, bowtie_mapped_directory)
sort_and_index(bowtie_mapped_directory, number_processors)
get_mapping_stats(number_processors, bowtie_mapped_directory)
get_mapping_stats_for_all(bowtie_mapped_directory, taxa_name)


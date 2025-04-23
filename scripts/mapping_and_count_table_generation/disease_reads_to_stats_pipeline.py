#!/usr/bin/env/python
import sys
import os
import re
import glob
import argparse
from os import listdir
from os.path import isfile, isdir, join


parser=argparse.ArgumentParser()

## use case:
## python /scratch/hammera/IGC/disease_data/workshop/scripts/disease_reads_to_stats_pipeline.py --processed_dir /scratch/hammera/IGC/disease_data/data/yu_cancer_data/ --out /scratch/hammera/IGC/disease_data/results/bt_mapping_results/yu_cancer_data/ --number_processors 40 --mapping_index /scratch/hammera/IGC/disease_data/data/bowtie_db/homosapiensIGC

##Read in the necessary arguments
parser.add_argument('--processed_dir', type=str, help='Directory of processed files')
parser.add_argument('--out', type=str,  help='Directory to write output to')
parser.add_argument('--number_processors', type=int, help='Number of processors')
parser.add_argument('--mapping_index', type=str, help='bt2 index location/name')
## parse the arguments which are supplied
args=parser.parse_args()

## assign the arguments to distinct variable names
## directory that contains info about read files
processed_dir = args.processed_dir
## writing everything out to this directory
out = args.out
## number of processors to be used
number_processors = args.number_processors
## igc to map to
mapping_index = args.mapping_index


## The number of threads that will be allocated for this script, note that this must be assigned from the command line
## if I get around to it consider setting the default number of threads to 1
os.environ["MKL_NUM_THREADS"] = str(number_processors)



def single_processing_function(clean_data_directory, number_proc, output_location, mapping_idx):
	import subprocess
	output = subprocess.check_output(str("ls -d " + clean_data_directory + "*R1_*"), shell=True)
	new_obj = output.split('\n')
	if new_obj[(len(new_obj)-1)] == '':
                new_obj.pop((len(new_obj)-1))
        for reads_file in new_obj:
		reads_file_2 = reads_file.replace("R1_", "R2_")
		reads_file_split = reads_file.split(str(clean_data_directory)[len(clean_data_directory)-9:len(clean_data_directory)])
		first_split_name = reads_file_split[1]
		simple_name = first_split_name.split("-s")[0]
		reusable_processing_name = str(output_location + simple_name)
		bowtie_sam_file_name = str(output_location + simple_name + ".sam")
		bowtie_mapping_command = ("/raid1/home/micro/hammera/bin/bowtie2-2.4.2-sra-linux-x86_64/bowtie2 -f " + "-k 1 " + "--met-file " + str(output_location + simple_name + ".txt") + " --threads " + str(number_proc) + " -x " + mapping_idx + " -1 " + reads_file + " -2 " + reads_file_2 + " -S " + bowtie_sam_file_name + str(" &> " + output_location + simple_name + ".log"))
                print(bowtie_mapping_command)
		os.system(bowtie_mapping_command)
		bowtie_bam_file_name = str(reusable_processing_name + ".bam")
		convert_sam_to_bam = str("/home/micro/hammera/bin/samtools-1.15/samtools view -bt --write-index -@ " + str(number_proc) + " " + bowtie_sam_file_name + " -o " + bowtie_bam_file_name)
		print(convert_sam_to_bam)
		os.system(convert_sam_to_bam)
		sorted_bam_name = bowtie_bam_file_name.replace('.bam', '_sorted.bam')
                samtools_sort = str("/home/micro/hammera/bin/samtools-1.15/samtools sort -@ " + str(number_proc) + " " + bowtie_bam_file_name + " -o " + sorted_bam_name)
                samtools_index = str("/home/micro/hammera/bin/samtools-1.15/samtools index -@ " + str(number_proc) + " " + sorted_bam_name)
                print(samtools_sort)
		print(samtools_index)
		os.system(samtools_sort)
                os.system(samtools_index)
                get_idxstats = str("/home/micro/hammera/bin/samtools-1.15/samtools idxstats -@ " + str(number_proc) + " " + sorted_bam_name + " > " + reusable_processing_name + "_idx_stats.txt")
		print(get_idxstats)
		os.system(get_idxstats)
		remove_extraneous_files = str("rm -f " + bowtie_sam_file_name + " " + bowtie_bam_file_name)
		print(remove_extraneous_files)
		os.system(remove_extraneous_files)
		remove_sorted_bam = str("rm -f " + sorted_bam_name)
		remove_sorted_bam_index = str("rm -f " + sorted_bam_name + ".bai")
		os.system(remove_sorted_bam)
		os.system(remove_sorted_bam_index)
	return None

def return_abbreviated_sample_name(sample_str, split_pattern, split_location):
	split_sample_name = sample_str.split(split_pattern)
	abbrev_sample_name = split_sample_name[split_location]
	return(abbrev_sample_name)

def get_mapping_stats_for_all(directory_of_idx_stats, stats_host_name):
	get_stats = str("python /raid1/home/micro/hammera/scripts/get_count_table.py " + directory_of_idx_stats + "*idx_stats.txt" + " > " + directory_of_idx_stats + stats_host_name + "_counts.txt")
	print(get_stats)
	os.system(get_stats)
	return None


single_processing_function(processed_dir, number_processors, out, mapping_index)

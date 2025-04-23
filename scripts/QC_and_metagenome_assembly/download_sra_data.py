#!/usr/bin/env python

import re
import sys
import pandas as pd
import csv
import os

file_of_fastqs = sys.argv[1]
output_directory = sys.argv[2]


lines = [line.rstrip() for line in open(file_of_fastqs)]

list_for_download = []

for i in lines:
		i_split = i.split(' ')
		if (len(i_split[2]) < 25):
			scientific_name = (i_split[0] + "_" + i_split[1] + "_" + i_split[2])
			split_files = i_split[3].split(';')
			list_for_download.append([scientific_name, split_files[0], split_files[1]])
		else:
			scientific_name = (i_split[0] + "_" + i_split[1])
                        split_files = i_split[2].split(';')
			list_for_download.append([scientific_name, split_files[0], split_files[1]])

names_list = [k[0] for k in list_for_download]
for j in names_list:
	print(j)




def build_directories_and_get_files(list_of_data, out_dir):
	for entry in list_of_data:
		scientific_name_length = len(entry[0].split('_'))
		wget_1 = ("wget " + entry[1] + " -P ")
		wget_2 = ("wget " + entry[2] + " -P ")
		if scientific_name_length > 2:
			split_taxa_name = entry[0]
			taxa_out_dir = (out_dir + split_taxa_name + "/")
			if (not(os.path.isdir(taxa_out_dir))):
				print(split_taxa_name)
				os.mkdir(taxa_out_dir)
				os.system(wget_1 + taxa_out_dir)
				os.system(wget_2 + taxa_out_dir)
			else:
				print(split_taxa_name)	
				os.system(wget_1 + taxa_out_dir)
                                os.system(wget_2 + taxa_out_dir)
		else:
			split_taxa_name = entry[0]
			taxa_out_dir = (out_dir + split_taxa_name + "/")
                        if (not(os.path.isdir(taxa_out_dir))):
                                print(split_taxa_name)
                                os.mkdir(taxa_out_dir)
                                os.system(wget_1 + taxa_out_dir)
                                os.system(wget_2 + taxa_out_dir)                
                        else:
                                print(split_taxa_name)
                                os.system(wget_1 + taxa_out_dir)
                                os.system(wget_2 + taxa_out_dir)



#build_directories_and_get_files(list_for_download, output_directory)

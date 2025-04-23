#!/usr/bin/env/python

import sys
import os
import re
import glob
from Bio.Align.Applications import MuscleCommandline

## The purpose of this function is to align the sequences which are put into fastas using the
## create_protein_alignment_files.py script. There's almost certainly a better way to write
## this, but I'll take care of that when I need to later on. 

## This requires a path to the fastas, then it outputs .aln files that contain the muscle alignment

folder_of_fastas_to_align  = sys.argv[1]
def align_with_muscle (path_to_fastas):
	os.chdir(str(path_to_fastas))
	for fasta_file in glob.glob("*.fasta"):
		muscle_exe = "/local/cluster/bin/muscle3.8.31_i86linux64"
		cline_please = MuscleCommandline(muscle_exe, input=fasta_file, out=((re.split("[.]", fasta_file)[0])+(".aln")))
		os.system(str(cline_please))

align_protein_seqs = align_with_muscle(folder_of_fastas_to_align)








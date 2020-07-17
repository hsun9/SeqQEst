#!/bin/bash

# Hua Sun
# 2/27/2019

# bash fastqc.sh -C config.ini -S sampleName -I sample.fastq -O path/outDIR
# -I input the file type is fastq.gz/fastq/bam/sam

# Bad QC https://www.bioinformatics.babraham.ac.uk/projects/fastqc/bad_sequence_fastqc.html

# getOptions
while getopts "C:S:I:O:" opt; do
  case $opt in
    C)
      CONFIG=$OPTARG
      ;;
    S)
      SAMPLE=$OPTARG
      ;;
    I)
      INPUT=$OPTARG
      ;;
    O)
      OUTDIR=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done


source ${CONFIG}


#FASTQC=/gscmnt/gc2737/ding/hsun/software/miniconda2/bin/fastqc
#Z7=/gscmnt/gc2737/ding/hsun/software/miniconda2/bin/7z


OUT=$OUTDIR/$SAMPLE
mkdir -p $OUT

$FASTQC -t 4 -o $OUT $INPUT
# output inputFileName_fastqc.zip & inputFileName_fastqc.html

# unzip the *fastqc.zip
# [NOTE]DO NOT change the -o$OUT
$Z7 x $OUT/*_fastqc.zip -o$OUT


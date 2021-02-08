#!/bin/bash

# Hua Sun
# 2018-11-29


#Usage
# bash bam.flagstat.sh -C config.ini -S sampleName -B path/bamfile.bam -O outDir
# -B bam/cram
# output: outDir/sampleName/

# set
#SAMTOOLS=/gscmnt/gc2737/ding/hsun/software/miniconda2/bin/samtools


# getOptions
while getopts "C:S:B:O:" opt; do
  case $opt in
    C)
      CONFIG=$OPTARG
      ;;
    S)
      SAMPLE=$OPTARG
      ;;
    B)
      BAM=$OPTARG
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


OUT=$OUTDIR/$SAMPLE
mkdir -p $OUT

# flagstat
$SAMTOOLS flagstat $BAM > $OUT/flagstat.txt


# stat
# the bam or cram should be done samtools index 
$SAMTOOLS stats $BAM | grep '^SN' > $OUT/bamStats.txt


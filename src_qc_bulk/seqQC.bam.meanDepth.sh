#!/bin/bash

# 2018-11-29

#Usage
# bash bam.avg_depth.sh -S sampleName -B path/bamfile.bam -O outDir
# -B bam/cram/sam
# output: outDir/sampleName/

# set
#SAMTOOLS=/gscmnt/gc3021/dinglab/hsun/software/miniconda2/bin/samtools


# getOptions
while getopts "C:S:B:O:" opt; do
  case $opt in
    C)
      CONFIG=$OPTARG
      ;;
    S)
      NAME=$OPTARG
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

source $CONFIG

OUT=$OUTDIR/$NAME
mkdir -p $OUT

# avg_depth
if [ -e $OUT/meanDepth.txt ]; then
	>&2 echo "The $OUT/meanDepth.txt exists!"
	exit 1
fi

$SAMTOOLS depth $BAM | awk '{sum+=$3; sumsq+=$3*$3} END {print "Sample =","'$NAME'"; print "Average_depth =",sum/NR; print "Stdev =",sqrt(sumsq/NR - (sum/NR)*(sum/NR))}' > $OUT/meanDepth.txt


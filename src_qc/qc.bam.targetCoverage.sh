#!/bin/bash

# Hua Sun
# 2/28/2019

#Usage
# bash bam.tcov.sh -N sampleName -B path/bamfile.bam -T target.interval_list -O outDir
# -B bam/cram
# -T target.interval_list (picard style)
# see Bed_toolkits
#    header from ref.dict
#    chr  start  end  + name
# output: outDir/sampleName/

# set
#JAVA=/gscmnt/gc2737/ding/hsun/software/jre1.8.0_152/bin/java
#PICARD=/gscmnt/gc2737/ding/hsun/software/picard.jar

#REF=/gscmnt/gc2560/core/model_data/2887491634/build21f22873ebe0486c8e6f69c15435aa96/all_sequences.fa
#TARGET=/gscmnt/gc2737/ding/hsun/data/human_genome/gencode_GRCh38_v29/gtf/proteinCoding.cds.merged.mgi_hg38.interval_list

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


source $CONFIG

OUT=$OUTDIR/$SAMPLE
mkdir -p $OUT

# target coverage
if [ -e $OUT/hsMetrics.txt ]; then
  echo "The $OUT/hsMetrics.txt exists!" >&2
  exit 1
fi

$JAVA -Xmx8G -jar $PICARD CollectHsMetrics \
   I=$BAM \
   O=$OUT/hsMetrics.txt \
   R=$GENOME \
   BAIT_INTERVALS=$TARGET \
   TARGET_INTERVALS=$TARGET


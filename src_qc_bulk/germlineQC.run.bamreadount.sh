#!/bin/bash

# Hua Sun
# 2019-09-04 updated 


# mgi
# sh bamReadcount.sh -C config.ini -S sampleName -L sample_loci.txt -B sample.bam -G reference_genome.fa -O outdir

# sample_loci.txt (must)
# chr start end ref alt 


#BAMREADCOUNT=/gscmnt/gc2525/dinglab/rmashl/Software/bin/bam-readcount/0.7.4/bam-readcount
#BRC2VAF=~/scripts/bamreadcount/script/bamReadcount2vaf.pl

#GENOME=/gscmnt/gc2737/ding/hsun/data/human_genome/gencode_GRCh38_v29/genome/GRCh38.primary_assembly.genome.fa

## getOptions
while getopts "C:S:L:B:G:O:" opt; do
  case $opt in
    C)
      CONFIG=$OPTARG
      ;;
    S)
      SAMPLE=$OPTARG
      ;;
    L)
      LOCI=$OPTARG
      ;;
    B)
      BAM=$OPTARG
      ;;
    G)
      GENOME=$OPTARG
      ;;
    O)
      OUTDIR=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done


# load contig.ini
source ${CONFIG}


OUT=$OUTDIR/brc
mkdir -p $OUT

awk '{print $1"\t"$2"\t"$2}' $LOCI | sort | uniq > $OUT/$SAMPLE.rc.loci
## make bamread count loci 
# SNV and InDel the end loci must set same with start, then it will automatically catch the indel
# chr start end(end must same as start)
# 21  10402985  10402985
# 21  10405200  10405200


# run bam-readcount --min-mapping-quality 10 --min-base-quality 20
$BAMREADCOUNT -q 10 -b 20 -f $GENOME -l $OUT/$SAMPLE.rc.loci $BAM > $OUT/$SAMPLE.rc

# call vaf 
perl $scriptDir/germlineQC.brc2vaf.pl -s $SAMPLE -l $LOCI $OUT/$SAMPLE.rc > $OUT/$SAMPLE.rc.vaf


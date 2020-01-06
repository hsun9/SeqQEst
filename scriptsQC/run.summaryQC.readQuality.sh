#!/bin/bash

# Hua Sun
# 10/24/2019


# output result to the DIR folder


DIR=$1
#DIR=/gscmnt/gc2522/dinglab/hsun/pdx/batch3/QC_raw_wxs


SCRIPT=~/scripts/bamQC/bamQC.sh

#research-hpc
#SUBMIT=~/pdxNet/hsun/Toolkit/LSF_mgi/lsf_submit.sh


# sometimes, the 'grep' does not work at all in MGI-server (9/17)
ls $DIR | sed 's/\///' | perl -ne 'print unless /^\./' | while read sample
do

   #sh $SUBMIT 8 1 sumQC.${sample} bash $SCRIPT -p summaryQC -n $sample -d $DIR
  echo [INFO] Summary QC - $sample ......
	
	sh $SCRIPT -p summaryQC -n $sample -d $DIR
	
done


echo [INFO] Merge summary QC ......

cat $DIR/*/summary.qc.out > $DIR/merged.summary.qc.tmp; head -n 1 $DIR/merged.summary.qc.tmp > $DIR/head.tmp; grep -v 'Total_reads' $DIR/merged.summary.qc.tmp > $DIR/merged.summary.qc.2.tmp; cat $DIR/head.tmp $DIR/merged.summary.qc.2.tmp > $DIR/merged.summary.qc.out; rm -f $DIR/*.tmp

# merge for single summary result to one
# cat */summary.qc.out > merged.summary.qc.tmp; head -n 1 merged.summary.qc.tmp > head.tmp; grep -v 'Total_reads' merged.summary.qc.tmp > merged.summary.qc.2.tmp; cat head.tmp merged.summary.qc.2.tmp > merged.summary.qc.out; rm -f *.tmp


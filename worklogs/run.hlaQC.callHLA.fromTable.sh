#!/bin/bash

# Hua Sun

SCRIPT=/gscmnt/gc2737/ding/hsun/github/SeqQEst/SeqQEst.sh
#research-hpc
SUBMIT=/gscmnt/gc3021/dinglab/hsun/Toolkit/LSF_mgi/lsf_submit.sh

CONFIG=/gscmnt/gc2737/ding/hsun/github/SeqQEst/config/config.gencode.ini


TABLE=''
OUTDIR="qc.hlaQC"

while getopts "C:T:O:" opt; do
  case $opt in
    C)
      CONFIG=$OPTARG
      ;;
    T)
      TABLE=$OPTARG
      ;;
    O)
      OUTDIR=$OPTARG
      ;;
  esac
done


# check table
if [[ $TABLE == '' ]];then
    echo [ERROR] Please set -T ...
    exit
fi


echo [CONFIG] ${CONFIG}
echo [TABLE] ${TABLE}


# OUTDIR
mkdir -p $OUTDIR


sed '1d' $TABLE | cut -f 1-3 | while read sample dataType bam
do

    if [ -e $bam ]; then
        sh $SUBMIT 32 1 hla.${sample} bash $SCRIPT -c ${CONFIG} -p qc3-hla -n $sample -t $dataType -b $bam -o ${OUTDIR}
    else
        echo [WARNING] Not exists BAM ... $bam 
        continue
    fi
    
done



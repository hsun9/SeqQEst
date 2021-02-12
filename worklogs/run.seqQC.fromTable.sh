#!/bin/bash

# Hua Sun

SCRIPT=/gscmnt/gc2737/ding/hsun/github/SeqQEst/SeqQEst.sh
#research-hpc
SUBMIT=/gscmnt/gc3021/dinglab/hsun/Toolkit/LSF_mgi/lsf_submit.sh

CONFIG=/gscmnt/gc2737/ding/hsun/github/SeqQEst/config/config.gencode.ini

TABLE=''
OUTDIR='qc.seqQC'

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



# output folder
outFolder=`pwd`/$OUTDIR
mkdir -p $outFolder



sed '1d' $TABLE | cut -f 1-3 | while read sample dataType bam
do
	
	# RNA
	if [[ $dataType == "RNA-Seq" ]]; then
		sh $SUBMIT 8 1 rna_fqc.${sample} bash $SCRIPT -c ${CONFIG} -p fastqc -n $sample -b $bam -o $outFolder
		sh $SUBMIT 8 1 rna_stat.${sample} bash $SCRIPT -c ${CONFIG} -p stat -n $sample -b $bam -o $outFolder
	fi
	
	# WXS
	if [[ $dataType == "WES" ]]; then
		sh $SUBMIT 8 1 wxs_fqc.${sample} bash $SCRIPT -c ${CONFIG} -p fastqc -n $sample -b $bam -o $outFolder
		sh $SUBMIT 8 1 wxs_stat.${sample} bash $SCRIPT -c ${CONFIG} -p stat -n $sample -b $bam -o $outFolder
		sh $SUBMIT 8 1 wxs_cov.${sample} bash $SCRIPT -c ${CONFIG} -p tarcov -n $sample -b $bam -o $outFolder
	fi
	
	# WGS
	if [[ $dataType == "WGS" ]]; then
		sh $SUBMIT 8 1 wgs_fqc.${sample} bash $SCRIPT -c ${CONFIG} -p fastqc -n $sample -b $bam -o $outFolder
		sh $SUBMIT 8 1 wgs_stat.${sample} bash $SCRIPT -c ${CONFIG} -p stat -n $sample -b $bam -o $outFolder
		sh $SUBMIT 8 1 wgs_depth.${sample} bash $SCRIPT -c ${CONFIG} -p depth -n $sample -b $bam -o $outFolder
	fi

done



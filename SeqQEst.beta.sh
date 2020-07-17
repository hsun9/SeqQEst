#!/bin/bash

# Author: Hua Sun
# Email: hua.sun@wustl.edu/hua.sun229@gmail.com

# beta version 0.2  4/26/2020



## USAGE: 

# sh SeqQEst.sh -c <config.ini> -p <pipelineName> -n <name> -o <outdir>

## INSTALL:
# python3.7
# python3 -m pip install pandas


##---------- QC-L1 (sequenceQC)
# fastqc
# sh SeqQEst.sh -p fastqc -n sample -b sample.bam -o outdir

# cov
# sh SeqQEst.sh -p tarcov -n sample -b sample.bam -o outdir

# flagstat & stat
# sh SeqQEst.sh -p stat -n sample -b sample.bam -o outdir

# summary QC
# sh SeqQEst.sh -p summaryQC -n sample -d dir

# plot for QC-L1
# sh SeqQEst.sh -p plot-qc1 -m matrix -n title -g groupname(WXS or RNA-Seq)



##---------- QC-L2 (germlineQC)
# bamreadcount (qc-l2.step-1)
# generate brc folder
# sh SeqQEst.sh -p qc2-brc -n sample -b sample.bam -o outdir

# merge vaf (qc-l2.step-2)
# generate  qc2.merged.vaf.table
# sh SeqQEst.sh -p qc2-merge -d dir_res_bamreadcount -o outdir

# qc-l2 summary (out plot & files)
# sampleInfo
# caseID      sampleID        dataType   group
# WU-L022   H_KU-322-D43A_1795_1    WES       PDX

# sh SeqQEst.sh -p qc2-summary -m matrix -f sampleInfo -o outdir

# plot for QC-L2
# sh SeqQEst.sh -p qc2-plot -m matrix -o outdir




##============================================================================##


outdir=`pwd`
config=''
loci=''

while getopts "c:l:p:n:m:f:g:b:d:o:" opt; do
  case $opt in
    c)
      config=$OPTARG
      ;;
    p)
      pipeline=$OPTARG
      ;;
    n)
      name=$OPTARG
      ;;
    l)
      loci=$OPTARG
      ;;    
    m)
      matrix=$OPTARG
      ;;
    g)
      group=$OPTARG
      ;;
    f)
      sampleInfo=$OPTARG
      ;;
    b)
      bam=$OPTARG
      ;;
    d)
      dir=$OPTARG
      ;;
    o)
      outdir=$OPTARG
      ;;
    \?)
      echo "script usage: $(basename $0) [-p] [-n] " >&2
      exit 1
      ;;
  esac
done


if [[ $config == '' ]]; then
  echo "[ERROR] Please set config.ini using -c ..." >&2
  exit
fi

if [ ! -e $config ]; then
  echo "[ERROR] No config file in $config ..." >&2
  exit
fi


source $config

# if the 'loci' not set then use default loci
if [[ $loci == '' ]];then loci=$MutLoci; fi


###############################
##     bam QC-L1 (sequenceQC)
###############################

##------------ fastqc
# input includes fastq.gz/fastq/bam/sam
if [[ $pipeline == "fastqc" ]]; then
  sh $scriptDir/qc.fastqc.sh -C ${config} -S ${name} -I ${bam} -O ${outdir}
fi

##------------ Target Coverage
if [[ $pipeline == "tarcov" ]]; then
  sh $scriptDir/qc.bam.targetCoverage.sh -C ${config} -S ${name} -B ${bam} -O ${outdir}
fi

##------------ Flagstat and Stat
if [[ $pipeline == "stat" ]]; then
  sh $scriptDir/qc.bam.flagstat.sh -C ${config} -S ${name} -B ${bam} -O ${outdir}
fi

##------------ Summary QC-L1
# manually merge all results
if [[ $pipeline == "summaryQC" ]]; then
  if [ -d $dir ]; then
    perl $scriptDir/qc.summary.bamQC.pl -n ${name} -f ${dir}/${name}/flagstat.txt -s ${dir}/${name}/bamStats.txt -m ${dir}/${name}/hsMetrics.txt --qc ${dir}/${name}/*_fastqc/summary.txt > ${dir}/${name}/summary.qc.out
  fi
fi


##------------ Plot - summary QC-L1
# manually merge all results
if [[ $pipeline == "plot-qc1" ]]; then
  #sh $scriptDir/qc.plot.summary.sh -M ${matrix} -F ${sampleInfo} -O {outdir}
  Rscript $scriptDir/qc.plot.summary.R --title ${name} --input ${matrix} --group ${group}
fi




###############################
##    bam QC-L2 (germlineQC)
###############################


##------------ Bamreadcount (QC-L2: step-1)
if [[ $pipeline == "qc2-brc" ]]; then
  sh $scriptDir/qc-L2.run.bamreadount.sh -C ${config} -L ${loci} -S ${name} -B ${bam} -O ${outdir}
fi

##------------ Merge the vaf from bamreadcount (QC-L2: step-2)
if [[ $pipeline == "qc2-merge" ]]; then 
  # the dir is *.vaf dir from bamreadcount
  sh $scriptDir/qc-L2.merge_vaf.table.sh -C ${config} -L ${loci} -D ${dir} -O ${outdir}
fi

##------------ Summary QC-L2 (QC-L2: step-3)
if [[ $pipeline == "qc2-summary" ]]; then
  mkdir -p $outdir
  
  # output - all cor.
  echo "[INFO] Calculate correlation ..." >&2
  python3 $scriptDir/qc-L2.cor_matrix4allSamples.py -i ${matrix} -o ${outdir}

    # Judge PASS/FAIL/swap
  echo "[INFO] Decision Pass/Fail/Swap ..." >&2
  python3 $scriptDir/qc-L2.judgeSamples_fromCorMatrix.py -i ${outdir}/all_of_corAllSamplesPair.tsv -a ${sampleInfo} -o ${outdir}
fi


if [[ $pipeline == "qc2-plot" ]]; then
  # plot-heatmap
  # need to add sort by caes function
  python3 $scriptDir/qc-L2.plot.summary.cor_heatmap.py -i ${matrix} -o ${outdir} --cluster
fi



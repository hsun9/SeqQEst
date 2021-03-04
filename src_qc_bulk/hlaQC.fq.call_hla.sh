#!/bin/bash

# Hua Sun
# 2021-03-01;
# bash run.sh -T dna -N sampleName -O ./OUT -B sample.bam

# -C config.ini
# -P bwa/razers3/optitype
# -N sampleName
# -T dna/rna
# -B *.bam
# -O outdir
# output outdir/sample/...


CONFIG=""

TYPE="dna"
pipeline="bwa"

while getopts "C:P:N:T:1:2:O:" opt; do
  case $opt in
    C)
      CONFIG=$OPTARG
      ;;
    P)
      pipeline=$OPTARG
      ;;
    N)
      NAME=$OPTARG
      ;;
    T)
      TYPE=$OPTARG
      ;;
    1)
      FQ1=$OPTARG
      ;;
    2)
      FQ2=$OPTARG
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


mkdir -p $OUTDIR

OUT=$OUTDIR/$NAME
mkdir -p $OUT


# load contig.ini
source ${CONFIG}



HLA_FASTA=''

if [[ $TYPE == "dna" ]] || [[ $TYPE == "DNA" ]] || [[ $TYPE == "WES" ]] || [[ $TYPE == "WGS" ]];then HLA_FASTA=$HLA_REF_DNA; fi
if [[ $TYPE == "rna" ]] || [[ $TYPE == "RNA" ]] || [[ $TYPE == "RNA-Seq" ]];then HLA_FASTA=$HLA_REF_RNA; fi




##===========================##
##       Set function
##===========================##

# set run OptiType function
run_optiType () {
    
    if [[ $TYPE == "dna" ]] || [[ $TYPE == "DNA" ]] || [[ $TYPE == "WES" ]] || [[ $TYPE == "WGS" ]]; then
        $OptiTypePipeline -i $OUT/$NAME.fished_1.fastq $OUT/$NAME.fished_2.fastq --dna -o $OUT --config ${config_for_optiType}
    fi

    if [[ $TYPE == "rna" ]] || [[ $TYPE == "RNA" ]] || [[ $TYPE == "RNA-Seq" ]]; then
        $OptiTypePipeline -i $OUT/$NAME.fished_1.fastq $OUT/$NAME.fished_2.fastq --rna -o $OUT --config ${config_for_optiType}
    fi
    
    exit 0
}



##===========================##
##       Main
##===========================##


##------------- OptiTypePipeline (only using it re-run optitype)
if [[ $pipeline == "optiType" ]]; then 
    n=`ls $OUT/*/*.tsv | wc -l`
    
    if [[ $n > 0 ]];then
        echo "[INFO] The $OUT/$NAME already exist HLA genotype ..." >&2
        exit 0
    fi
    
    run_optiType
    exit 0
fi



##------------- bwa
if [[ $pipeline == "bwa" ]]; then
    # R1
    $BWA mem -t 8 $HLA_FASTA $FQ1 | $SAMTOOLS view -Shb -F 4 -o $OUT/$NAME.fished_1.bam -
    $SAMTOOLS bam2fq $OUT/$NAME.fished_1.bam > $OUT/$NAME.fished_1.fastq

    ## remove temp file 
    rm -f $OUT/$NAME.fished_1.bam


    # R2
    $BWA mem -t 8 $HLA_FASTA $FQ2 | $SAMTOOLS view -Shb -F 4 -o $OUT/$NAME.fished_2.bam -
    $SAMTOOLS bam2fq $OUT/$NAME.fished_2.bam > $OUT/$NAME.fished_2.fastq

    ## remove temp file 
    rm -f $OUT/$NAME.fished_2.bam

    # run OptiType
    run_optiType
fi



#rm -f $OUT/$NAME.fished_1.fastq $OUT/$NAME.fished_2.fastq



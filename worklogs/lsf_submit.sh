#!/bin/sh

## USAGE
## sh lsf_submit.sh <memory int> <threads int> <any name> <any command>

MEM=$1;shift
THREADS=$1;shift
NAME=$1;shift

DIR=`pwd`
mkdir -p $DIR/logs

bsub -q research-hpc -M ${MEM}000000 -n ${THREADS} -R "select[mem>${MEM}000] span[hosts=1] rusage[mem=${MEM}000]" -oo $DIR/logs/${NAME}.log -eo $DIR/logs/${NAME}.err -a "docker(registry.gsc.wustl.edu/genome/genome_perl_environment)" "$@"



#  Author: Hua Sun
#  Email: hua.sun@wustl.edu/hua.sun229@gmail.com

# 2019-09-04 updated


# sh run.sh -C <config.ini> -L <loci.txt> -D <data_dir> -O <outdir>

#loci=$1
#dir=$2
#outdir=$3


# getOptions
while getopts "C:L:D:O:" opt; do
  case $opt in
    C)
      CONFIG=$OPTARG
      ;;
    L)
      LOCI=$OPTARG
      ;;
    D)
      DIR_VAF=$OPTARG
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


## loci
# chr1  179551371 179551371 A C
# chr1  67395837  67395837  A G

mkdir -p $OUTDIR

tmp_dir=$OUTDIR/tmp_dir_vaf

mkdir -p $tmp_dir

# get loci
cut -f 1-2 ${LOCI} | perl -pe 's/\t/_/' | perl -pe 's/^/loci\n/ if $.==1' > $tmp_dir/loci
# loci
# chr1_1001

sed '1d' $tmp_dir/loci > $tmp_dir/loci.noHeader

ls $DIR_VAF/*.vaf | perl -pe 's/.*\///' | perl -pe 's/\.rc\.vaf$//' | while read sample
do

  # to remove false positive & keep more rna-seq value, if total read < 6 or alt < 3 then the vaf set to 0
  #TWDE-100-1301-M1513986_1        chr1    10413143        10413143        G       A       130     81      49      37.69
  perl -ne 'chomp; @F=split/\t/; $F[9]=0 if ($F[6]<6 || $F[8]<3); print join("\t", @F)."\n"' $DIR_VAF/$sample.*.vaf | awk -F['\t'] '{print $2"_"$3"\t"$10}' | perl -pe 's/^/'$sample'\n/ if $.==1' > $tmp_dir/$sample.vaf

  # call loci matching one because sometimes the loci hasn't called by bamreadcound
  perl $scriptDir/germlineQC.key2row.pl $tmp_dir/loci.noHeader $tmp_dir/$sample.vaf -showListAll -uniq -o $tmp_dir/$sample.all_loci.vaf
  cut -f 3 $tmp_dir/$sample.all_loci.vaf | perl -pe 's/^/'$sample'\n/ if $.==1' > $tmp_dir/$sample.all_loci.h.vaf

done


paste $tmp_dir/loci $tmp_dir/*.all_loci.h.vaf > ${OUTDIR}/qc2.snp.merged_vaf.table

# replace 'NA' by 0
perl -i -pe 's/\tNA/\t0/g if $.>1' ${OUTDIR}/qc2.snp.merged_vaf.table


rm -rf $tmp_dir

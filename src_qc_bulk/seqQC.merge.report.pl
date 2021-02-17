=head1 VERSION

  Hua Sun
  
  2020-11-11 v0.2

    Do summary results
      samtools.flagstat.txt
      samtools.stats.txt
      picard.hsMetrics.txt
      fastqc - "summary.txt"   # from fastqc folder
    

=head1 USAGE

    perl seqQC.summary.report.pl -n samplename -f flagstat.txt -s stat.txt -m hsMetrics.txt -d meanDepth.txt -qc fastqc.summary.txt > output
    
    perl seqQC.summary.report.pl -n samplename -f flagstat.txt > output
    perl seqQC.summary.report.pl -n samplename -f flagstat.txt -s stat.txt > output
    perl seqQC.summary.report.pl -n samplename -s stat.txt > output
    perl seqQC.summary.report.pl -n samplename -qc fastqc.summary.txt > output
    perl seqQC.summary.report.pl -n samplename -m hsMetrics.txt > output
    perl seqQC.summary.report.pl -n samplename -d meanDepth.txt > output
    

  INPUT
  *.flagstat (samtools flastat input.bam)

  OUTPUT (-f,-s,-m)
  Sample Total_reads Mapped(%) MappedReads(M) Duplicates(%) AverageReadsLength(bp)  MaximumReadsLength(bp)  MeanMappingQuality  AverageInsertSize(bp)   MeanTargetCoverage


  OUTPUT -f flagstat.txt
  Sample Total_reads Mapped(%) MappedReads(M) Duplicates(%)

  OUTPUT -s stat.txt
  AverageReadsLength(bp)    MaximumReadsLength(bp)  MeanMappingQuality  AverageInsertSize(bp)

  OUTPUT -qc fastqc/summary.txt
  Basic_Statistics  Per_base_sequence_quality   Per_tile_sequence_quality   Per_sequence_quality_scores Per_base_sequence_content   Per_sequence_GC_content Per_base_N_content  Sequence_Length_Distribution    Sequence_Duplication_Levels Overrepresented_sequences   Adapter_Content
  
  OUTPUT -m hsMetrics.txt
  MeanTargetCoverage

  OUTPUT -d meanDepth.txt
  MeanDepth_for_WGS

=cut


use strict;
use Getopt::Long;

my $samplename = '';
my $flagstatF = '';
my $statsF = '';
my $hsMetricsF = '';
my $fastqc_sumF = '';
my $meanDepthF = '';
my $help;
GetOptions(
    "n:s" => \$samplename,
    "f:s" => \$flagstatF,
    "s:s" => \$statsF,
    "m:s" => \$hsMetricsF,
    "d:s" => \$meanDepthF,
    "qc:s" => \$fastqc_sumF,
    "help" => \$help
);


die `pod2text $0` if ($help);


my $title = '';
my $value = '';

my $flag = 0;  # flag run qc numbers

# flagstat.txt
if ($flagstatF ne ''){

    my $total_reads = 'NA';
    my $mapped_perc = 'NA';
    my $mapped_reads = 'NA';
    my $dup_perc = 'NA';
    

    if( -e $flagstatF ){

        my @data = `cat $flagstatF`;
        my ($qc_passed, $qc_failed, $qc_passed_perc, $dup);
        
        foreach (@data){
            # total
            if (/(\d+) \+ (\d+) in total/){
                $qc_passed = $1;
                $qc_failed = $2;
                $total_reads = $qc_passed + $qc_failed;
                $qc_passed_perc = sprintf("%.2f", 100*$qc_passed/$total_reads);     
                next;
            }

            # duplicated
            if (/(\d+) \+ \d+ duplicates/){
                $dup = $1;
                $dup_perc = sprintf("%.2f", 100*$dup/$total_reads);
                next;
            }   
    
            # mapped %
            if (/^(\d+) \+ \d+ mapped \(([\d.]+)\%/){
                $mapped_reads = $1/1000000;     # format to Million
                $mapped_perc = $2;
                next;
            }   
        }

    } else {
        `echo [WARNING] Flagstat file does not exist ... >&2`;
    }


    $title = "Sample\tTotal_reads\tMapped(%)\tMappedReads(M)\tDuplicates(%)\t";
    $value = "$samplename\t$total_reads\t$mapped_perc\t$mapped_reads\t$dup_perc\t";
    
    ++$flag;

}



# stats.txt
if ($statsF ne ''){

    my $avgReadsL = 'NA';
    my $maxReadsL = 'NA';
    my $avgQuality = 'NA';
    my $avgInsertSize = 'NA';

    if( -e $statsF ){

        my @data = `cat $statsF`;
        
        foreach (@data){
            # average length
            if (/average length\:\t(\d+)/){
                $avgReadsL = $1;
                next;
            }
        
            # maximum length
            if (/maximum length\:\t(\d+)/){
                $maxReadsL = $1;
                next;
            }

            # average quality
            if (/average quality\:\t([\d.]+)/){
                $avgQuality = $1;
                next;
            }   
    
            # insert size average
            if (/insert size average\:\t([\d.]+)/){
                $avgInsertSize = $1;
                next;
            }   
        }

    } else {
        `echo [WARNING] Stats file does not exist ... >&2`;
    }


    # if the first time
    if ($flag == 0){
        $title = "Sample\t";
        $value = "$samplename\t";
        ++$flag;
    }
    
    $title .= "AverageReadsLength(bp)\tMaximumReadsLength(bp)\tMeanMappingQuality\tAverageInsertSize(bp)\t";
    $value .= "$avgReadsL\t$maxReadsL\t$avgQuality\t$avgInsertSize\t";

}




# hsMetrics.txt
if ($hsMetricsF ne ''){

    my $fmt_avgTarCov = 'NA';

    if( -e $hsMetricsF ){

        my $avgTarCov = `awk 'NR==8' $hsMetricsF | cut -f 23`;
        chomp($avgTarCov);
    
        $fmt_avgTarCov = sprintf("%.2f", $avgTarCov);

    } else {
        `echo [WARNING] hsMetrics file does not exists ... >&2`;
    }


    # if the first time
    if ($flag == 0){
        $title = "Sample\t";
        $value = "$samplename\t";
        ++$flag;
    }
    
    $title .= "MeanTargetCoverage(MQ20)\t";
    $value .= "$fmt_avgTarCov\t";
    
}




# MeanDepth.txt
if ($meanDepthF ne ''){

    my $depth = 'NA';

    if( -e $meanDepthF ){
        
        # mean depth
        $depth = `awk 'NR==2' $meanDepthF | cut -d' ' -f3`;
        chomp($depth);

    } else {
        `echo [WARNING] Mean depth file does not exists ... >&2`;
    }

            # if the first time
    if ($flag == 0){
        $title = "Sample\t";
        $value = "$samplename\t";
        ++$flag;
    }

    $title .= "MeanDepth_for_WGS\t";
    $value .= "$depth\t";
    
}





# fastqc.summary.txt
if ($fastqc_sumF ne ''){

    my @arr = `cut -f 1-2 $fastqc_sumF`;
    
    # if the first time
    if ($flag == 0){
        $title = "Sample\t";
        $value = "$samplename\t";
    }   

    my ($val, $catalog) = @_;
    foreach (@arr){
        chomp;
        next if ($_ eq '');
        
        ($val, $catalog) = split("\t");
        
        $catalog =~ s/ /_/g;
        
        $title .= "$catalog\t";
        $value .= "$val\t";
    }

}


##---------- final output
$title =~ s/\t$//;
$value =~ s/\t$//;

print "$title\n";
print "$value\n";

exit;


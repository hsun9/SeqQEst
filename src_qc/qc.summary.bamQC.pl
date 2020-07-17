=head1 VERSION

  Hua Sun

  01/22/2019 -- v1.2
  07/06/2019 -- v1.3 add mapping-reads

	Do summary results
	  samtools.flagstat.txt
	  samtools.stats.txt
	  picard.hsMetrics.txt
	  fastqc - "summary.txt"   # from fastqc folder
	

=head1 USAGE

	perl summary.bamQC.pl -n samplename -f flagstat.txt -s stat.txt -m hsMetrics.txt -qc fastqc.summary.txt > output
	
	perl summary.bamQC.pl -n samplename -f flagstat.txt > output
	perl summary.bamQC.pl -n samplename -f flagstat.txt -s stat.txt > output
	perl summary.bamQC.pl -n samplename -s stat.txt > output
	perl summary.bamQC.pl -n samplename -qc fastqc.summary.txt > output
	perl summary.bamQC.pl -n samplename -m hsMetrics.txt > output
	

  INPUT
  *.flagstat (samtools flastat input.bam)

  OUTPUT (-f,-s,-m)
  Sample Total_reads Mapped(%) MappedReads(M) Duplicates(%) AverageReadsLength(bp)	MaximumReadsLength(bp)	MeanMappingQuality	AverageInsertSize(bp)	MeanTargetCoverage


  OUTPUT -f flagstat.txt
  Sample Total_reads Mapped(%) MappedReads(M) Duplicates(%)

  OUTPUT -s stat.txt
  AverageReadsLength(bp)	MaximumReadsLength(bp)	MeanMappingQuality	AverageInsertSize(bp)

  OUTPUT -qc fastqc/summary.txt
  Basic_Statistics	Per_base_sequence_quality	Per_tile_sequence_quality	Per_sequence_quality_scores	Per_base_sequence_content	Per_sequence_GC_content	Per_base_N_content	Sequence_Length_Distribution	Sequence_Duplication_Levels	Overrepresented_sequences	Adapter_Content
  
  OUTPUT -m hsMetrics.txt
  MeanTargetCoverage

=cut


use strict;
use Getopt::Long;

my $samplename = '';
my $flagstatF = '';
my $statsF = '';
my $hsMetricsF = '';
my $fastqc_sumF = '';
my $help;
GetOptions(
	"n:s" => \$samplename,
	"f:s" => \$flagstatF,
	"s:s" => \$statsF,
	"m:s" => \$hsMetricsF,
	"qc:s" => \$fastqc_sumF,
	"help" => \$help
);


die `pod2text $0` if ($help);


my $title = '';
my $value = '';

my $flag = 0;  # flag run qc numbers

# flagstat.txt
if ($flagstatF ne ''){

	my @data = `cat $flagstatF`;
	my ($qc_passed, $qc_failed, $total_reads, $qc_passed_perc);
	my ($dup, $dup_perc, $mapped_perc);
	my $mapped_reads;
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
	
	$title = "Sample\tTotal_reads\tMapped(%)\tMappedReads(M)\tDuplicates(%)\t";
	$value = "$samplename\t$total_reads\t$mapped_perc\t$mapped_reads\t$dup_perc\t";
	
	++$flag;

}



# stats.txt
if ($statsF ne ''){

	my @data = `cat $statsF`;
	my ($avgReadsL, $maxReadsL, $avgQuality, $avgInsertSize);
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
	
	# if the first time
	if ($flag == 0){
		$title = "Sample\t";
		$value = "$samplename\t";
	}
	
	$title .= "AverageReadsLength(bp)\tMaximumReadsLength(bp)\tMeanMappingQuality\tAverageInsertSize(bp)\t";
	$value .= "$avgReadsL\t$maxReadsL\t$avgQuality\t$avgInsertSize\t";
	
	++$flag;
}



# hsMetrics.txt
if ($hsMetricsF ne ''){

	my $avgTarCov = `awk 'NR==8' $hsMetricsF | cut -f 23`;
	chomp($avgTarCov);
	
	my $fmt_avgTarCov = sprintf("%.2f", $avgTarCov);
	
	# if the first time
	if ($flag == 0){
		$title = "Sample\t";
		$value = "$samplename\t";
	}
	
	$title .= "MeanTargetCoverage(MQ20)\t";
	$value .= "$fmt_avgTarCov\t";
	
	++$flag;
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


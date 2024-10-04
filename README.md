SeqQEst
========

Quality control for next-generation sequencing data

Author: Hua Sun  
Version: v1.02

* Updated (2021-03-20)
* Updated (2021-03-01)
	* v1.02 -- Add `hlaQC.fq.call_hla.sh`

* Previous version
	* Version v1.0: https://github.com/ding-lab/SeqQEst/tree/v1.0
	* Beta version: https://github.com/ding-lab/SeqQEst/tree/beta-version



Introduction
-------------
SeqQEst is a tool to estimate single- and multiple-sample sequence quality, to detect swapped, mislabeled, or contaminated samples, and to confirm genetic lineages through consideration of bulk DNA- and RNA-seq data. 



Requirements
-------------

### Install (conda)
	
Install below tools by "sh setup/setup_tools.sh"

The "setup_tools.sh" will install tools and output `config_seqQEst.ini`, which will list all of tool locations.

```	
    	JRE v1.8
    	Picard >=v2.17.11
    	Samtools >=v1.5
    	FastQC >=v0.11.9
    	7z >=v15.09
    	Bam-readcount v0.7.4
    	BWA v0.7.17
    	OptiType v1.3.2
    
    	Python 3.x (>=3.7)
	    	Pandas v1.2.1
	    	Matplotlib v3.3.4
	    	Seabornd v0.11.1
		Perl >=v5.18.2
```


### Set database

* Genome *.fa
	* GENCODE GRCh38
	
	[Note] The pipeline was tested using GENCODE_GRCh38_v29 reference

* Target interval_list form (qc1 - WES coverage)
	* https://gatk.broadinstitute.org/hc/en-us/articles/360035531852-Intervals-and-interval-lists
	* Refer to interval_list/proteinCoding.cds.merged.gencode_hg38_v29.interval_list

* SNP loci (qc2)
	* See folder loci/

* HLA database (qc3)
	* See folder data/
	* Source: https://github.com/FRED-2/OptiType/tree/master/data



### Set config

* Set "set_optiType.ini" (set razers3 location)
* Set "config.ini", please refer to config/config.demo.ini
* Please refer to 'setup/setup.sh' output `config_seqQEst.ini` to set 



Input
-------------
* BAM
	* WGS
	* WES
	* RNA-Seq

* FASTQ
	* HLA-QC is able to use input as BAM or fastq.gz 

* Table of bam/sample info
	* bam.catalog (Form)
		> The table uses for running cohort

		```
		ID   DataType   Bam
		TWDE-M1511917 WES /path/PDX/TWDE-M1511917.bam
      	```
      	```
      	[Note]
      	DataType: WGS/WES/RNA-Seq
		```
		
	* sample.info (Form)
		> The table uses for summary of qc2 & qc3

		```
		CaseID	ID	NewID	DataType	Group
       WU12	TWDE242	WU12.WES.N	WES	Human_Normal
       WU59	TWDE4639	WU59.WES.P2	WES	PDX
       ```
       
       ```
       [Note]
       CaseID: Case ID
       ID: Data ID
       DataType: WGS/WES/RNA-Seq
       Group: Human_Normal/Human_Tumor/PDX
       NewID: If there is no short name then set as '.'
			
		```


Output
-------------

* SeqQC

	```
	qc.SeqQC/
		qc1.seq.summary.merged.out        # summary report
	```

* GermlineQC

	```
	qc.germlineQC/
	summary_germlineQC/
		report.summary_germlineQC.out     # summary report
		all_of_corAllSamplesPair.tsv
		export_corr_matrix.tsv
		report.germlineQC.potential.swap_data.out
		...
	```

* HLA-QC

	```
	qc.hlaQC/
	summary_hlaQC/
		report.summary_hlaQC.out          # summary report
		report.hla_with_info.out
	```


Usage
-------------

```
sh SeqQEst.sh -c <config.ini> -p <pipelineName> -n <name> -b <bam> -o <outdir>


Tip: If you don’t want to set “contig.ini” repeatedly, then you can set it inside the "SeqQEst.sh".

e.g.
open "SeqQEst.sh" and set 
config="/fullpath/config.ini"

sh SeqQEst.sh -p <pipelineName> -n <name> -b <bam> -o <outdir>

```


#### SeqQC (qc1)

```
# fastqc
sh SeqQEst.sh -p fastqc -n sampleName -b sample.bam -o qc.seqQC

# cov for WES
sh SeqQEst.sh -p tarcov -n sampleName -b sample.bam -o qc.seqQC

# depth (use for WGS)
sh SeqQEst.sh -p meanDepth -n sampleName -b sample.bam -o qc.seqQC

# flagstat & stat
sh SeqQEst.sh -p stat -n sampleName -b sample.bam -o qc.seqQC

# merge seqQC results
sh SeqQEst.sh -p qc1-merge -d qc.seqQC

# qc1 summary and plot
sh SeqQEst.sh -p qc1-summary -m matrix.tsv -f sample.info -o summary_seqQC

```

#### GermlineQC (qc2)

```
# call bamreadcount
sh SeqQEst.sh -p qc2-brc -n sample -b sample.bam -o qc.germlineQC

# qc2 merge
sh SeqQEst.sh -p qc2-merge -d qc.germlineQC/brc -o qc.germlineQC

# qc2 summary
sh SeqQEst.sh -p qc2-summary -f sample.info -m qc2.snp.merged_vaf.table -o summary_germlineQC

# plot for qc2
sh SeqQEst.sh -p qc2-plot -m matrix.tsv -o summary_germlineQC

```

#### HLA-QC (qc3)

```
# qc3 call hla (-t dna/rna) - bam
sh SeqQEst.sh -p qc3-hla -n samplename -t dna -b sample.bam -o qc.hlaQC

# qc3 call hla (-t dna/rna) - fastq
sh SeqQEst.sh -p qc3-hla -n samplename -t dna -1 r1.fastq.gz -2 r2.fastq.gz -o qc.hlaQC


# qc3 merge
sh SeqQEst.sh -p qc3-merge -d qc.hlaQC -o qc.hlaQC

# qc3 summary
sh SeqQEst.sh -p qc3-summary -f sample.info -m qc3.hla.merged.out -o summary_hlaQC

```


#### Tutorial: Run multiple samples in cluster

```
MGI-Server (LSF)
[Note] Three of QCs are independent. Hence you can run all programs at the same time.
	
1. Data Processing
	
	* SeqQC
	> Input  : bam.catalog.table
	> Output : qc.seqQC
	sh worklogs/run.seqQC.fromTable.sh -T ./demo.bam.catalog.table
	
	* GermlineQC
	> Input  : bam.catalog.table
	> Output : qc.germlineQC/brc
	sh worklogs/run.germlineQC.callSNPs.fromTable.sh -T ./demo.bam.catalog.table
	
	* HLA-QC
	> Input  : bam.catalog.table
	> Output : qc.hlaQC
	sh worklogs/run.hlaQC.callHLA.fromTable.sh -T ./demo.bam.catalog.table




2. Summary Report (Table)
	
	* SeqQC
	> Input  : qc.seqQC
	> Output : qc.seqQC/qc1.seq.summary.merged.out
	sh SeqQEst.sh -p qc1-merge -d ./qc.seqQC
	
	> Input  : 1. qc.seqQC/qc1.seq.summary.merged.out
	           2. sample.info 
	> Output : summary_seqQC/report.summary_seqQC.out
	sh SeqQEst.sh -m qc.seqQC/qc1.seq.summary.merged.out -f sample.info -o summary_seqQC
	
	
	* GermlineQC
	> Input  : qc.germlineQC/brc
	> Output : qc.germlineQC/qc2.snp.merged_vaf.table
	sh SeqQEst.sh -p qc2-merge -d qc.germlineQC/brc -o qc.germlineQC
	
	> Input  : 1. qc.germlineQC/qc2.snp.merged_vaf.table
	           2. sample.info 
	> Output : summary_germlineQC/report.summary_germlineQC.out
	sh SeqQEst.sh -p qc2-summary -m qc.germlineQC/qc2.snp.merged_vaf.table -f sample.info -o summary_germlineQC
	
	# plot
	sh SeqQEst.sh -p qc2-plot -m summary_germlineQC/export_corr_matrix.tsv -o summary_germlineQC
	
	
	* HLA-QC
	> Input  : qc.hlaQC
	> Output : qc.hlaQC/qc3.hla.merged.out
	sh SeqQEst.sh -p qc3-merge -d qc.hlaQC -o qc.hlaQC
	
	> Input  : 1. qc.hlaQC/qc3.hla.merged.out
	           2. sample.info
	> Output : summary_hlaQC/report.summary_hlaQC.out
	sh SeqQEst.sh -p qc3-summary -f sample.info -m qc.hlaQC/qc3.hla.merged.out -o summary_hlaQC


```

The first manuscript using this tool
-------------
Hua Sun, et al., Nat Commun 2021. Comprehensive characterization of 536 patient-derived xenograft models prioritizes candidates for targeted treatment.

Contact
-------------
Hua Sun, <hua.sun229@gmail.com>; Li Ding (PI) <lding@wustl.edu>



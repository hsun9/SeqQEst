SeqQEst
========

Quality control for next-generation sequencing data

Author: Hua Sun  
Version: v1.0  


* Previous version
	* Beta version: https://github.com/ding-lab/SeqQEst/tree/beta-version



Introduction
-------------
SeqQEst is a tool to estimate single- and multiple-sample sequence quality, to detect swapped, mislabeled, or contaminated samples, and to confirm genetic lineages through consideration of all available DNA- and RNA-seq data. 



Requirements
-------------

### Install

    JRE v1.8
    Picard v2.17.11
    Samtools v1.5
    FastQC v0.11.9
    7z v15.09
    Bam-readcount v0.7.4
    BWA v0.7.17
    OptiType v1.3.2
    
    Python 3.x (>=3.7)
	    Pandas
	    Matplotlib
	Perl v5.18.2
	R v3.5.1


### Set database

* Genome *.fa
	* GENCODE GRCh38 

* Target interval_list form
	* https://gatk.broadinstitute.org/hc/en-us/articles/360035531852-Intervals-and-interval-lists

* SNP loci
	* See folder loci/
	* Note: The public loci will be uploaded after the paper is submitted. 

* HLA database
	* See folder data/



### Set config
	
Please refer to config/config.demo.ini



Input
-------------
* BAM
	* WGS
	* WES
	* RNA-Seq
	
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



Usage
-------------

```
sh SeqQEst.sh -c <config.ini> -p <pipelineName> -n <name> -o <outdir>


Tip: To conveniently use commend line, the config.ini location sets into the SeqQEst.sh code.

e.g.
open "SeqQEst.sh" and set 
config="/fullpath/config.ini"

sh SeqQEst.sh -p <pipelineName> -n <name> -o <outdir>

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

# summary QC
sh SeqQEst.sh -p qc1-summary -d qc.seqQC

# plot for QC-L1
sh SeqQEst.sh -p qc1-plot -m matrix.tsv -n title -g groupname(WXS or RNA-Seq)

```

#### GermlineQC (qc2)

```
# call bamreadcount
sh SeqQEst.sh -p qc2-brc -n sample -b sample.bam -o qc.germlineQC

# merge vaf
# generate  qc2.merged.vaf.table
sh SeqQEst.sh -p qc2-merge -d qc.germlineQC/brc -o qc.germlineQC

# qc-l2 summary (out plot & text)
# //sampleInfo
# CaseID  ID  NewID   DataType    Group
# C0012 S242-242-03 .   WES Human_Normal
# C0059 S4639   .  WES PDX


sh SeqQEst.sh -p qc2-summary -m matrix.tsv -f sample.info -o qc.germlineQC

# plot for QC-L2
sh SeqQEst.sh -p qc2-plot -m matrix.tsv -o qc.germlineQC

```

#### HLA-QC (qc3)

```
# qc-l3 call hla (-t dna/rna)
sh SeqQEst.sh -p qc3-hla -n samplename -t dna -b sample.bam -o qc.hlaQC

# qc-l3 merge
sh SeqQEst.sh -p qc3-merge -d qc.hlaQC -o qc.hlaQC

# qc-l3 summary
sh SeqQEst.sh -p qc3-summary -f sample.info -m hlaQC.merged.out -o .

```

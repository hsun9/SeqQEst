
# Hua Sun

# Rscript qc.plot.summary.R --title title --type WXS --input merged.summary.qc.out


library(GetoptLong)

group = "WXS"
GetoptLong(
	"title=s", "title",
	"group=s", "seq. data type WXS/RNA-Seq",
	"input=s", "input matrix"
)


d <- read.table(input, sep = "\t", header = T) 


pdf(paste0(title, ".summary.qc-L1.pdf"), width = 6, height = 3.5, useDingbats=FALSE)


##======================== Coverage


library(ggplot2)


if (group == "WXS"){

  ggplot(d, aes(x = Sample, y = MeanTargetCoverage.MQ20.)) +
      	geom_bar(stat = "identity", fill = "#99ccff") +
     		theme_classic() + 
        aes(x=reorder(Sample, -MeanTargetCoverage.MQ20.), y=MeanTargetCoverage.MQ20.) + 
     #   coord_flip() + 
        labs(x="Samples", y="Mean target coverage (MQ20)") +
        geom_hline(yintercept = 20, linetype="dashed", color = "red") +
        geom_hline(yintercept = 50, linetype="dashed", color = "blue") + 
     #   theme(axis.text.x = element_text(angle = 90, hjust = 1))
     		theme(axis.text.x=element_blank(), axis.ticks.x=element_blank()) +
     #		ylim(0, 500) + 
     		ggtitle(title)
     		
}

if (group == "RNA-Seq"){

  ggplot(d, aes(x = Sample, y = MappedReads.M.)) +
      	geom_bar(stat = "identity", fill = "#FFBB00") +
     		theme_classic() + 
        aes(x=reorder(Sample, -MappedReads.M.), y=MappedReads.M.) + 
     #   coord_flip() + 
        labs(x="Samples", y="Mapped Reads (Mbp)") +
        geom_hline(yintercept = 20, linetype="dashed", color = "red") +
        geom_hline(yintercept = 50, linetype="dashed", color = "blue") + 
     #   theme(axis.text.x = element_text(angle = 90, hjust = 1))
     		theme(axis.text.x=element_blank(), axis.ticks.x=element_blank()) +
     #		ylim(0, 500) + 
     		ggtitle(title)
     		
}


#pdf(paste0(title, ".cov.pdf"), width = 6, height = 3.5, useDingbats=FALSE)
#print(p_cov)
#dev.off()



##======================== FastQC

fqc <- d[,11:dim(d)[2]]
rownames(fqc) <- d$Sample

library(plyr)

fqc_fmt <- as.data.frame(apply(fqc, 1, function(x) as.numeric(mapvalues(x, c("PASS", "WARN", "FAIL"), c(2, 1, 0)))))
rownames(fqc_fmt) <- colnames(fqc)


library(pheatmap)

pheatmap(fqc_fmt, 
					border_color = NA,
					#border_color = "#F8F8F8",
					cluster_rows = F, 
					cluster_cols = F, 
					show_colnames = F,
					legend = F,
					color = colorRampPalette(c("#fc9272", "#ffeda0", "#a1d99b"))(3),   # red, yellow, green
					cellheight = 6, 
				#	cellwidth = 5,
					fontsize = 6
					)


dev.off()



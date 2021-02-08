
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#%matplotlib inline
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d','--data', help='input data frame')
parser.add_argument('-t','--dataType', help='data type')
parser.add_argument('-o','--outdir', default='.', help='out dir')

args = parser.parse_args()

#f_in = '../data_info/washU.rcc.used.xlsx'



'''
	Main
'''
def main():
	df = pd.read_csv(args.data, sep='\t')

	# WES
	if args.dataType == 'WES':
		# coverage
		outfile = f'{args.outdir}/qc.wxs.cov.pdf'
		scatterPlot('WES', df, 'Sample', 'MeanTargetCoverage(MQ20)', outfile)

	# RNA-Seq
	if args.dataType == 'RNA-Seq':
		# mapping reads depth
		outfile = f'{args.outdir}/qc.rna-seq.depth.pdf'
		scatterPlot('RNA-Seq', df, 'Sample', 'MappedReads(M)', outfile)




'''
	Set function
'''
def scatterPlot(title, df, x, y, outfile):
    sampleSize = df.shape[0]

    
    df.sort_values(by=[y]).plot.scatter(x=x, y=y)

    plt.title(title)
    plt.xlabel('Sample size n=' + str(sampleSize))
    
    plt.xticks('')    # hide x-axis
    plt.ylim(0, )  # Limits for the Y axis
    
    plt.axhline(y=50, color='g', linestyle='-') # add line
    plt.axhline(y=20, color='r', linestyle='-') # add line
    
    
    plt.savefig(outfile)




if __name__ == '__main__':
	main()







"""
	
	Author: Hua Sun
    Email: hua.sun@wustl.edu/hua.sun229@gmail.com
	
	06/23/2019,09/4/2019
	
	
  Usage:
  	python3 run.py -i matrix -o outdir
  
  Options:
  	-i <matrix>    # input matrix
  	-o <outdir>    # output directory
  	--showVal      # show cor value in heatmap
  	--showName     # show col & row names in heatmap

  	
  Output:
  	export_cor.dataframe.tsv
  	cor_plot.pdf
  	
"""

import argparse

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#%matplotlib inline


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", metavar="FILE", type=str, help="input matrix")
parser.add_argument("-o", "--outdir", metavar="Folder", type=str, default = os.getcwd(), help="output directory")
parser.add_argument("--showVal", action='store_true', help="show cor value in heatmap")
parser.add_argument("--showName", action='store_true', help="show col & row names in heatmap")
                  
args = parser.parse_args()


def main():
	# read file
	df = pd.read_csv(args.input, sep = "\t")
	
	sns.set(font_scale=.5)

#	print('[Making] ... ' + args.outdir + '/' + 'export_cor.cluster.pdf')
#	p = ''
#	p = sns.clustermap(cor, cmap='coolwarm', metric="correlation", xticklabels=args.showName, yticklabels=args.showName, annot=args.showVal)
#	p.savefig(args.outdir + '/' + 'export_cor.cluster.pdf', transparent=True)

	print('[Making] ... ' + args.outdir + '/' + 'export_cor.heatmap.pdf')
	p2 = ''
	p2 = sns.heatmap(cor, cmap='coolwarm', xticklabels=args.showName, yticklabels=args.showName, annot=args.showVal, vmin=0, vmax=1)
	p2.figure.savefig(args.outdir + '/' + 'export_cor.heatmap.pdf', transparent=True)





# run main()
if __name__ == '__main__':
	main()





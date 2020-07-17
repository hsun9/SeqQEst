
"""
    
    Author: Hua Sun
    Email: hua.sun@wustl.edu/hua.sun229@gmail.com
    
    06/23/2019,09/4/2019
    
    
  Usage:
    python3 run.py -i matrix -o outdir

    # matrix
            TWBU-HPB_117-D117-03    TWBU-HPB_117-D117-06    TWBU-HPB_117-D117-06-XT2
    TWBU-HPB_117-D117-03    1   0.984971165 0.315429592
    TWBU-HPB_117-D117-06    0.984971165 1   0.330193182
    TWBU-HPB_117-D117-06-XT2    0.315429592 0.330193182 1

    # rename_table
    ID  NewID  (table must including two column names)

  
  Options:
    -i <matrix>      # input matrix
    -o <outdir>      # output directory
    --showVal        # show cor value in heatmap
    --showName       # show col & row names in heatmap
    --rename <table> # rename for samples in plot


    
  Output:
    export_cor.dataframe.tsv
    cor_plot.pdf
    
"""

import argparse

import os
import os.path
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#%matplotlib inline


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", metavar="FILE", type=str, help="input matrix")
parser.add_argument("-o", "--outdir", metavar="Folder", type=str, default = os.getcwd(), help="output directory")
parser.add_argument("--cluster", action='store_true', help="show cluster")
parser.add_argument("--showVal", action='store_true', help="show cor value in heatmap")
parser.add_argument("--showName", action='store_true', help="show col & row names in heatmap")
parser.add_argument("--rename", metavar="FILE", type=str, default="", help="rename sample names")
parser.add_argument("--font_size", type=float, default=0.6, help="font size")
                  
args = parser.parse_args()



def check_file(file):
    if not os.path.isfile(file):
        message = '[Error] File not exists ...' + str(file)
        sys.exit(message)


def main():
    # read file
    check_file(args.input)

    df = pd.read_csv(args.input, sep = "\t")
    df.index = df.iloc[:,0].tolist()
    df.drop(df.columns[0], axis=1, inplace = True)
    
    df = df.fillna(0) # NA to 0

    # rename for samples, if set --rename
    if args.rename != "":
        check_file(args.rename)
        
        df_sampleInfo = pd.read_csv(args.rename, sep="\t")
        df_sampleInfo = df_sampleInfo[~df_sampleInfo.NewID.isin(['NA', '.', '', '-'])]
        
        dic_name = dict(zip(df_sampleInfo.ID, df_sampleInfo.NewID))

        # do rename 
        df.rename(columns=dic_name, index=dic_name, inplace=True)


        #dic_name = {}
        #with open(args.rename) as f:
        #    for line in f:
        #        (key, val) = line.split("\t")
        #        dic_name[key] = val
        #df.rename(columns=dic_name, index=dic_name, inplace = True)

    
#   plt.subplots(figsize=(32, 30))

    sns.set(font_scale = args.font_size)  # set based font size

    if args.cluster:

        outpdf_name = 'export_cor.cluster.heatmap.pdf'
        if args.rename != "":
            outpdf_name = 'export_cor.cluster.heatmap.reanamed.pdf'

        print('[Making] ... ' + args.outdir + '/' + outpdf_name)
    
        plt.rcParams['font.size'] = 5

        g = sns.clustermap(df, 
                    cmap='coolwarm',
                    annot=args.showVal,
                    annot_kws={'size':10},   # value size
                    cbar=True,
                    square= True,
                    cbar_kws={'label': 'Correlation'}
                    )

        g.savefig(args.outdir + '/' + outpdf_name, transparent=True)


    else:

        outpdf_name = 'export_cor.heatmap.pdf'
        if args.rename != "":
            outpdf_name = 'export_cor.heatmap.reanamed.pdf'

        print('[Making] ... ' + args.outdir + '/' + 'export_cor.heatmap.pdf')
    
        plt.rcParams['font.size'] = 5

        g = sns.heatmap(df, 
                    cmap='coolwarm',
                    annot=args.showVal,
                    annot_kws={'size':10},
                    cbar=True,
                    square= True,
                    cbar_kws={'label': 'Correlation'}
                    )
        g.figure.axes[-1].yaxis.label.set_size(10)
        g.figure.savefig(args.outdir + '/' + outpdf_name, transparent=True)



# run main()
if __name__ == '__main__':
    main()





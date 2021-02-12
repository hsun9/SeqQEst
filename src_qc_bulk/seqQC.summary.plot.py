'''
    Hua Sun

    2019-11-04

    Plot for qc.SeqQC summary data

    DataType: WGS/WES/RNA-Seq

    python3 seqQC.summary.plot.py -d qc.seqQC.tsv --info sample.info -o outdir 


'''


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-d','--data', help='input data frame')
parser.add_argument('--info', help='sample info')
parser.add_argument('-o','--outdir', default='.', help='out dir')

args = parser.parse_args()



'''
    Main
'''
def main():
    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    df = pd.read_csv(args.data, sep='\t')
    info = pd.read_csv(args.info, sep='\t')

    df_merge = pd.merge(df, info, left_on='Sample', right_on='ID', how='left')


    for dataType in df_merge['DataType'].unique():
        
        if dataType == 'WGS':
            df_tar = df_merge.loc[df_merge['DataType']=='WGS', ['ID', 'MeanDepth_for_WGS']]
        
        if dataType == 'WES':
            df_tar = df_merge.loc[df_merge['DataType']=='WES', ['ID', 'MeanTargetCoverage(MQ20)']]
                    
        if dataType == 'RNA-Seq':
            df_tar = df_merge.loc[df_merge['DataType']=='WGS', ['ID', 'MappedReads(M)']]
        
        if df_tar.shape[0] > 0:
            PlotDepth(df_tar, dataType, args.outdir)



'''
    Set function
'''

def PlotDepth(df, dataType, outdir):
    
    df = df.sort_values(by=df.columns.values[1], ascending=False)

    title = ''
    ylabel = ''

    if dataType == 'WGS':
        title = 'WGS data'
        ylabel = 'Mean depth'

    if dataType == 'WES':
        title = 'WES data'
        ylabel = 'Mean target coverage (MQ20)'

    if dataType == 'RNA-Seq':
        title = 'RNA-Seq data'
        ylabel = 'Mean reads (M)'

    sampleSize = df.shape[0]

    plt.plot(df.iloc[:,0], df.iloc[:,1], 'o', markersize=4)
    
    plt.title(title)
    plt.xlabel(f'Sample size n={sampleSize}')
    plt.ylabel(ylabel)
    
    plt.xticks('')
    plt.ylim(0, )
    
    plt.axhline(y=50, color='g', linestyle='-')
    plt.axhline(y=20, color='r', linestyle='-')
    
    outfile = f'{outdir}/qc.seqQC.{dataType}.pdf'

    plt.savefig(outfile)



if __name__ == '__main__':
    main()






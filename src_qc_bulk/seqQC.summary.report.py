'''
    Hua Sun

    2021-03-21; 2021-02-15; 2019-11-04

    Plot for qc.SeqQC summary data

    python3 seqQC.summary.report.py -d qc.seqQC.tsv --info sample.info -o outdir 

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
    # output merged info data
    df_merge.to_csv(f'{args.outdir}/report.seqQC_with_info.out', sep='\t', index=False)


    df_rec = pd.DataFrame(columns=['Sample', 'DataType', 'LowMappingPercentage', 'LowDepth', 'LowMappingQuality', 'LowInsertSize', 'AdapterContent'])

    for sample in df_merge['Sample'].unique():
        row = df_merge.loc[df_merge['Sample']==sample]
        rec = JudgePerSample(sample, row)
        df_rec = df_rec.append(rec, ignore_index=True)

    # output summary report
    df_rec.to_csv(f'{args.outdir}/report.summary_seqQC.out', sep='\t', index=False)


    # plot
    for dataType in df_merge['DataType'].unique():
        
        if dataType == 'WGS':
            df_tar = df_merge.loc[df_merge['DataType']=='WGS', ['ID', 'MeanDepth_for_WGS']]
        
        if dataType == 'WES':
            df_tar = df_merge.loc[df_merge['DataType']=='WES', ['ID', 'MeanTargetCoverage(MQ20)']]
                    
        if dataType == 'RNA-Seq':
            df_tar = df_merge.loc[df_merge['DataType']=='RNA-Seq', ['ID', 'MappedReads(M)']]
        
        if df_tar.shape[0] > 0:
            PlotDepth(df_tar, dataType, args.outdir)



'''
    Set function
'''

## Judge per sample
def JudgePerSample(sample, row):
    dataType = row['DataType'].values[0]
    
    map_percent = row['Mapped(%)'].values[0]
    
    mapped_reads = row['MappedReads(M)'].values[0]
    mean_cov = row['MeanTargetCoverage(MQ20)'].values[0]
    depth_wgs = row['MeanDepth_for_WGS'].values[0]

    map_quality = row['MeanMappingQuality'].values[0]
    avgInsert = row['AverageInsertSize(bp)'].values[0]
    adapter = row['Adapter_Content'].values[0]
    # 'DataType', 'LowMappingPercentage', 'LowDepth', 'LowMappingQuality', 'LowInsertSize', 'AdapterContent'

    # map percentage
    if map_percent < 90:
        LowMappingPercentage = f'Yes({map_percent})'
    else:
        LowMappingPercentage = 'No'
    
    # map reads -- avg 88M RNA, WES 100x, WGS 20x
    LowDepth = 'No'
    if mapped_reads < 50:
        if dataType == 'RNA-Seq' and mean_cov > 50:
            LowDepth = f'Yes({int(mapped_reads)}M)'

        if dataType == 'WES':
            if mean_cov > 50:
                LowDepth = 'No'
            else:
                LowDepth = f'Yes({int(mean_cov)}x)'
        
        if dataType == 'WGS':
            if mean_cov > 10:
                LowDepth = 'No'
            else:
                LowDepth = f'Yes({int(depth_wgs)}x)'
    else:
        if dataType == 'WES' and mean_cov < 50:
            LowDepth = f'Yes({int(mean_cov)}x)'
        elif dataType == 'WGS' and depth_wgs < 10:
            LowDepth = f'Yes({int(depth_wgs)}x)'
        else:
            LowDepth = 'No'

    # map_quality -- avg WES 35; RNA 36
    if map_quality < 20:
        LowMappingQuality = f'Yes({int(map_quality)}x)'
    else:
        LowMappingQuality = 'No'

    # insersion_size -- avg WES 225; RNA 1063
    LowInsertSize = 'No'
    if dataType == 'WES' and avgInsert < 150:
        LowInsertSize = f'Yes({int(avgInsert)})'

    if dataType == 'WGS'  and avgInsert < 150:
        LowInsertSize = f'Yes({int(avgInsert)})'

    if dataType == 'RNA-Seq' and avgInsert < 800:
        LowInsertSize = f'Yes({int(avgInsert)})'
    

    rec = {'Sample':sample, 'DataType':dataType, 'LowMappingPercentage':LowMappingPercentage, 'LowDepth':LowDepth,
         'LowMappingQuality':LowMappingQuality, 'LowInsertSize':LowInsertSize, 'AdapterContent':adapter}


    return rec





## Plot
def PlotDepth(df, dataType, outdir):
    print(df.shape)
    df = df.sort_values(by=df.columns.values[1], ascending=False)
    mean_val = int(df.iloc[:,1].mean())
    x_max = df.shape[0]
    y_max = df.iloc[:,1].max()

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

    plt.plot(df.iloc[:,0], df.iloc[:,1], 'o', markersize=2)
    
    plt.title(title)
    plt.xlabel(f'Sample size n={sampleSize}')
    plt.ylabel(ylabel)
    
    plt.xticks('')
    plt.ylim(0, )
    
    plt.axhline(y=50, color='g', linestyle='-')
    plt.axhline(y=20, color='r', linestyle='-')

    plt.text(x_max*0.8, y_max*0.8, f'Mean={mean_val}')

    
    outfile = f'{outdir}/qc.seqQC.{dataType}.pdf'

    plt.savefig(outfile)

    plt.close()




if __name__ == '__main__':
    main()






"""

  Author: Hua Sun
  Email: hua.sun@wustl.edu/hua.sun229@gmail.com
  
  v0.1.2 2020-11-16
  
  Calculate cor for all samples
  
  USAGE:
  python3 germlineQC.call_correlation.py -i <vaf_matrix> -o <outdir>
  -i matrix
  -r renameList (if set -r then sample name will rename)
  --show_pair_cor
  -o outdir

"""

import argparse
import pandas as pd
import numpy as np
import re
import os



# collect input arguments
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", metavar="FILE", type=str, help="input VAF table")
parser.add_argument("-r", "--renameList", metavar="FILE", type=str, default = '', help="input VAF table")
parser.add_argument("--show_pair_cor", action='store_true', help='show pair cor file')
parser.add_argument("-o", "--outdir", type=str, default = os.getcwd(), help='Output dirction')

args = parser.parse_args()

'''
    Main
'''

# pair sample cor main
def main():
    
    # read files
    df = pd.read_csv(args.input, sep = "\t")
    
    df.index = df.iloc[:,0].tolist()
    
    # Remove duplicate columns (based on column name)
    df = df.loc[:, ~df.columns.str.replace("(\.\d)$", "").duplicated()]

    # replace new name if args.renameList available
    if args.renameList != '':
        Func_CheckFile(args.rename)
        df_sampleInfo = pd.read_csv(args.renameList, sep="\t")
        df_sampleInfo = df_sampleInfo[~df_sampleInfo.NewID.isin(['NA', '.', '', '-'])]

        name_dict = dict(zip(df_sampleInfo.ID, df_sampleInfo.NewID))

        # do rename 
        df.rename(columns=name_dict, inplace=True)


    df = df.fillna(0)

    df_cor = df.corr(method='pearson')
    df_cor = df_cor.fillna(0)

    # output all of correlation matrix
    print('[Making] ... ' + args.outdir + '/' + 'export_corr_matrix.tsv')
    df_cor.index.name='Name'
    df_cor.to_csv(args.outdir + '/export_corr_matrix.tsv', sep = "\t")
    

    # run output pair-cor
    if args.show_pair_cor:
        print('[Making] ... ' + args.outdir + '/' + 'all_of_corAllSamplesPair.tsv')
        Func_ExtractPairCor(df_cor)


'''
    Set Functions
'''


# set check arguments
def Func_CheckArguments():
    if args.input is None:
        raise ValueError('Must specify a VAF matrix with -i flag.')


def Func_CheckFile(file):
    if not os.path.isfile(file):
        message = '[Error] File not exists ...' + str(file)
        sys.exit(message)



# set calculate cor. between samples from cor N x N matrix
def Func_ExtractPairCor(df_cor):
    n = len(df_cor.columns)
    colNames = df_cor.columns
    rowNames = df_cor.index
    
    new_dict = {}
    
    for i in range(0, n):
        row_name = rowNames[i]
        
        for k in range(i+1, n):
            val = df_cor.iloc[i,k]
            
            # if cor is null then replace as 0
            if pd.isnull(val):
                val = 0
            
            col_name = colNames[k]
            pair_name = row_name + '--' + col_name
                        
            new_dict[pair_name] = [val]
    
    # output
    # sample1--sample2 caseID cor status
    if bool(new_dict):
        dfObj = pd.DataFrame.from_dict(new_dict, orient = 'index')
        dfObj.columns = ['Cor']
        dfObj.index.name='Pair'
        dfObj.to_csv(args.outdir + '/all_of_corAllSamplesPair.tsv', sep = "\t")
    else:
        print("[WARNING] No content for the dictionary!")




if __name__ == '__main__':
    # check file
    Func_CheckArguments()
    # call cor for all of samples
    main()


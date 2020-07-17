"""

  Author: Hua Sun
  Email: hua.sun@wustl.edu/hua.sun229@gmail.com
  
  11/27/2019 v0.2
  
  Calculate cor for all samples
	
	USAGE:
  	Rscript cor_group.py -i <vaf_matrix> -o <outdir>
  
  INPUT:
    # the colname must not like sample.1 (should like sample_1 or sample-1)
  	loci	C_01_1055_051_S_D1031238.T	C_01_1055_051_S_D25A_4926.PDX	C_01_1055_051_S_T25C_1405.PDX.RNA
		chr1_100206504	100	100	100
		chr1_1046489	4.02	1.33	0
		chr1_108937356	0	0.62	0
  
  OUTPUE:
  	 all_of_corAllSamples.tsv
  	 all_of_corAllSamplesPair.tsv

"""

import argparse
import pandas as pd
import numpy as np
import re
import os


# collect input arguments
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", metavar="FILE", type=str, help="input VAF table")
parser.add_argument("-o", "--outdir", type=str, default = os.getcwd(), help='Output dirction')

args = parser.parse_args()



# set check arguments
def func_checkArguments():
    if args.input is None:
        raise ValueError('Must specify a VAF matrix with -i flag.')




# pair sample cor main
def func_calCor():
    
    # read files
    df = pd.read_csv(args.input, sep = "\t")
    
    df.index = df.iloc[:,0].tolist()
    
    # Remove duplicate columns (based on column name)
    # 'a', 'a.1' --> 'a'
    df = df.loc[:, ~df.columns.str.replace("(\.\d)$", "").duplicated()]
    # https://www.interviewqs.com/ddi_code_snippets/remove_duplicate_cols
    #df = df.loc[:,~df.columns.duplicated()]

    df.fillna(0)

    df_cor = df.corr(method='pearson')
    # output all of correlation matrix
    print('[Making] ... ' + args.outdir + '/' + 'export_corr_matrix.tsv')
    df_cor.to_csv(args.outdir + '/export_corr_matrix.tsv', sep = "\t", index = True, header = True)
    
    # run output pair-cor
    print('[Making] ... ' + args.outdir + '/' + 'all_of_corAllSamplesPair.tsv')
    func_extractPairCor(df_cor)



# set calculate cor. between samples from cor N x N matrix
def func_extractPairCor(df_cor):
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
        dfObj.to_csv(args.outdir + '/all_of_corAllSamplesPair.tsv', sep = "\t", index = True, header = True)
    else:
        print("[WARNING] No content for the dictionary!")




if __name__ == '__main__':
    # check file
    func_checkArguments()
    # call cor for all of samples
    func_calCor()


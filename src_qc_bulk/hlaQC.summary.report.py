"""

    Author: Hua Sun
    Email: hua.sun@wustl.edu/hua.sun229@gmail.com
  
    v0.1.1 2020-11-22
    v0.1   2020-11-09
  
    Make sample report for HLA-QC

  
    USAGE:
    python3 hlaQC.summary.report.py --info sample.info --hla <merged.hla.table> -o <outdir>

    -i|--info <file>  sample info file
    --hla <file>      merged hla file
    -o [str]          outdir

"""

import argparse
import pandas as pd
import numpy as np
import re
import os
import sys


# collect input arguments
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--info", required=True, type=str, help="info table")
parser.add_argument("--hla", required=True, type=str, help="hla file")
parser.add_argument("-o", "--outdir", type=str, default = os.getcwd(), help='Output dirction')

args = parser.parse_args()



'''
    Main
'''

def main():
    Check_File(args.info)
    Check_File(args.hla)

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    df_hla = pd.read_csv(args.hla, sep='\t')
    df_info = pd.read_csv(args.info, sep='\t', usecols=range(0,2))
    df_info.columns=['CaseID', 'ID']

    # merge hla with info
    df_info_with_hla = pd.merge(df_info, df_hla.iloc[:,:7], left_on='ID', right_on='Sample', how='outer')
    df_info_with_hla.drop(columns='Sample', inplace=True)
    # output hla + sample info
    df_info_with_hla.to_csv(f'{args.outdir}/report.hla_with_info.out', sep='\t', index=False)

    # summary hla by case
    outfile = f'{args.outdir}/report.summary_hlaQC.out'
    Make_SummaryReport_for_HLA(df_hla, df_info, outfile)
    
    



'''
    Set Functions
'''

# check file
def Check_File(file):
    if not os.path.isfile(file):
        message = '[Error] File not exists ...' + str(file)
        sys.exit(message)

def Check_Dir(dir):
    if not os.path.isdir(dir):
        message = '[Error] Directory not exists ...' + str(dir)
        sys.exit(message)



# HLA file
def Make_SummaryReport_for_HLA(df_hla, df_info, outfile):
    # 1. extract sample and hla
    df_hla2 = df_hla.iloc[:,:7]
    # Sample	A1	A2	B1	B2	C1	C2

    # 2. remove dup hla & sort
    df_hla2.set_index(['Sample'], inplace=True)
    sampleList = df_hla2.index.values
    hla_list = df_hla2.values.tolist()
    df_new = pd.DataFrame(columns=['ID', 'HLA'])
    df_new['ID'] = sampleList
    df_new['HLA'] = hla_list
    df_new['HLA'] = df_new['HLA'].apply(lambda x: sorted(list(set(x))))
    

    # 3. add sample info
    df_info = df_info.merge(df_new, on='ID', how='outer')
    # notice info
    Summary_CheckInfo(df_info)

    df_info = df_info[df_info['CaseID'].notna()]
    # NaN to unknwon
    df_info['HLA'] = df_info['HLA'].fillna(value="Unknown")


    # 4. summary
    df_info['HLA'] = df_info['HLA'].astype(str)
    report_hla = df_info.groupby(['CaseID', 'HLA']).size().reset_index(name="MatchedHLA_dataSize")
    totalSampleSize = df_info[['CaseID', 'ID']].groupby('CaseID').size().reset_index(name="TotalDataSize")
    report_hla = report_hla.merge(totalSampleSize, on='CaseID', how='left')
    report_hla['AlienDataName'] = '.'
    report_hla.to_csv(f'{outfile}.log', sep='\t', index=False)
    # CaseID  HLA  MatchedHLA_dataSize  TotalDataSize AlienDataName
    
    # hla dict
    dict_hla_sample = MakeDictionary(df_info[['HLA', 'ID']])
    # case dict
    dict_case_sample = MakeDictionary(df_info[['CaseID', 'ID']])

    SeekAlienSample(df_info, report_hla, dict_hla_sample, dict_case_sample, outfile)

   


# Make_SummaryReport_for_HLA - sub part-1
def Summary_CheckInfo(info):
    total_case = len(info['CaseID'].unique())
    with_hla = info.dropna(subset=['HLA']).shape[0]
    print(f'[INFO] Total CaseID: {total_case}')
    print(f'[INFO] Data with HLA info: {with_hla}')  
    
    null_case = info['CaseID'].isnull().sum()
    null_hla = info['HLA'].isnull().sum()
    print(f'[INFO] Numbers of Empty CaseID: {null_case}')  
    print(f'[INFO] Data without HLA: {null_hla}')




# Make_SummaryReport_for_HLA - sub part-2
def MakeDictionary(df):
    # HLA ID
    hla_dict = {}

    # case group sample
    for i in df.index:
        key = str(df.iloc[i,0])
        val = str(df.iloc[i,1])
        
        if key in hla_dict:
            hla_dict[key].append(val)
        else:
            hla_dict[key] = [val]

    return hla_dict




# Make_SummaryReport_for_HLA - sub part-3
def SeekAlienSample(df_info, report, dict_hla, dict_case, outfile):

    report['ID_mix'] = report['HLA'].apply(lambda x: dict_hla.get(x))
    # CaseID  HLA  MatchedHLA_dataSize  TotalDataSize AlienDataName IDs

    # summary
    summary_report = pd.DataFrame(columns=['CaseID', 'TotalDataSize', 'HLA', 'MathedHLA_data', 'NotMathedHLA_data', 'No_HLA', 'AlienDataName'])

    for case_name in report.CaseID.unique():
        
        df_per_case = report.loc[report.CaseID==case_name]
        
        total_data_size = df_per_case.TotalDataSize.values[0]
        no_hla = df_per_case.loc[df_per_case.HLA=='Unknown'].shape[0]

        if df_per_case.shape[0]>1:
            max_val = max(df_per_case.MatchedHLA_dataSize.values.tolist())

            if max_val == 1:
                hla = 'Mixed'
                matched_hla_data = 1
                not_matched_hla_data = 'Ambiguity'

                alien_name = 'Ambiguity'
            else:
                hla = df_per_case.loc[df_per_case.MatchedHLA_dataSize==max_val, 'HLA'].values[0]
                matched_hla_data = max_val
                not_matched_hla_data = total_data_size - matched_hla_data - no_hla

                mixedID = df_per_case.loc[df_per_case.MatchedHLA_dataSize!=max_val, 'ID_mix'].tolist()
                flat_list = [item for sublist in mixedID for item in sublist]
                sampleList = df_info.loc[df_info['CaseID']==case_name, 'ID'].values.tolist()
                
                alien_name = list(set(flat_list) & set(sampleList))
        else:
            hla = df_per_case.HLA.values[0]
            matched_hla_data = df_per_case.MatchedHLA_dataSize.values[0]
            not_matched_hla_data = 0

            alien_name = df_per_case.AlienDataName.values[0]
            

        
        rec = {'CaseID':case_name, 'TotalDataSize':total_data_size,
                'HLA':hla, 'MathedHLA_data':matched_hla_data, 'NotMathedHLA_data':not_matched_hla_data, 'No_HLA':no_hla, 'AlienDataName':alien_name}
        summary_report = summary_report.append(rec, ignore_index=True)


    # summary output
    summary_report.to_csv(outfile, sep='\t', index=False)
    





if __name__ == '__main__':
    main()


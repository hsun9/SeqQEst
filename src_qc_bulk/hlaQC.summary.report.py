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
    Summary_CheckInfo(df_info)
    df_info = df_info[df_info['CaseID'].notna()]
    # NaN to unknwon
    df_info['HLA'] = df_info['HLA'].fillna(value="Unknown")
    
    # hla dict
    dict_hla_sample = MakeDictionary(df_info[['HLA', 'ID']])
    # case dict
    dict_case_sample = MakeDictionary(df_info[['CaseID', 'ID']])

    # 4. summary
    df_info['HLA'] = df_info['HLA'].astype(str)
    report_hla = df_info.groupby(['CaseID', 'HLA']).size().reset_index(name="MatchedHLASample")
    totalSampleSize = df_info[['CaseID', 'ID']].groupby('CaseID').size().reset_index(name="TotalSample")
    report_hla = report_hla.merge(totalSampleSize, on='CaseID', how='left')
    report_hla['AlienSample'] = '.'
    
    SeekAlienSample(report_hla, dict_hla_sample, dict_case_sample, outfile)

   


# Make_SummaryReport_for_HLA - sub part-1
def Summary_CheckInfo(info):
    total_case = len(info['CaseID'].unique())
    print(f'[INFO] Total CaseID: {total_case}')
    
    null_case = info['CaseID'].isnull().sum()
    null_hla = info['HLA'].isnull().sum()

    print(f'[INFO] Numbers of Empty CaseID: {null_case}')  
    print(f'[INFO] Numbers of Empty HLA: {null_hla}')




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
def SeekAlienSample(report, dict_hla, dict_case, outfile):
    # sort
    report.sort_values(by=['CaseID', 'MatchedHLASample'], ascending=False, inplace=True)
    report['Not_MatchedHLASample'] = 0

    # summary
    summary_report = pd.DataFrame(columns=['CaseID', 'TotalSample', 'HLA', 'MatchedHLASample',  'Not_MatchedHLASample', 'AlienSample'])

    for key in report.index:
        caseID = ''.join(report.loc[report.index==key, 'CaseID'].values)
        
        if caseID in list(summary_report.CaseID.values):

            #if report['HLA'][report.index==key].values == 'nan':
            #    continue

            hla_from_org_report = ''.join(report['HLA'][report.index==key].values)
            sample_id = dict_hla.get(hla_from_org_report)
            
            # find target sample
            if len(sample_id) > 1:
                # double check from target case
                targetSampleList = dict_case.get(caseID)
                sample_id = list(set(targetSampleList) & set(sample_id))

            sample_id = ','.join(sample_id)

            # add AlienSample
            if summary_report.loc[summary_report.CaseID==caseID, 'Not_MatchedHLASample'].values > 0:
                summary_report.loc[summary_report.CaseID==caseID, 'Not_MatchedHLASample'] = summary_report.loc[summary_report.CaseID==caseID, 'Not_MatchedHLASample'].values + int(report.loc[report.index==key, 'MatchedHLASample'].values)
                summary_report.loc[summary_report.CaseID==caseID, 'AlienSample'] = summary_report.loc[summary_report.CaseID==caseID, 'AlienSample'] + ',' + sample_id
            else:
                summary_report.loc[summary_report.CaseID==caseID, 'Not_MatchedHLASample'] = int(report.loc[report.index==key, 'MatchedHLASample'].values)
                summary_report.loc[summary_report.CaseID==caseID, 'AlienSample'] = sample_id
        else:
            rec = report.loc[report.index==key, ['CaseID', 'TotalSample', 'HLA', 'MatchedHLASample', 'Not_MatchedHLASample', 'AlienSample']]
            summary_report = summary_report.append(rec, ignore_index=True)


    # summary output
    summary_report.to_csv(outfile, sep='\t', index=False)
    





if __name__ == '__main__':
    main()


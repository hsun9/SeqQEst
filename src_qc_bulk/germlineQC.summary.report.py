"""

    Author: Hua Sun
    Email: hua.sun@wustl.edu/hua.sun229@gmail.com
    
    v0.1.1 2020-11-22
    v0.1   2020-11-16
    beta   2019-11-24

    python3 germlineQC.summary.report.py -i export_corr_matrix.tsv -a anno.file -o outdir

"""

import argparse
import os
import io
import pandas as pd
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, help="input matrix")
parser.add_argument("-a", "--anno", required=True, help="sample anno")
parser.add_argument("-o", "--outdir", default='./germlineQC_result', help="output directory")

args = parser.parse_args()


# start time
start_time = datetime.datetime.now()
print ('[INFO] Running summary-report ... ', start_time.strftime("%Y-%m-%d %H:%M:%S"))


# make directory
path = args.outdir

try:
    if not os.path.isdir(path):
        os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)




'''
    Main
'''

def main():
    info = pd.read_csv(args.anno, sep='\t', usecols=range(0,4))
    info.columns = ['CaseID', 'ID', 'NewID', 'DataType']
    df = pd.read_csv(args.input, sep='\t', index_col=0)
    

    #CaseID  ID  NewID   DataType    Group 
    ## 1. record the not matching sample info data
    CheckDataInfo(info, df, path)

    ## 2. make dict for sample - data type
    new_datatype = ReplaceListValue_forStr(info['DataType'], 'WES', 'DNA')
    new_datatype = ReplaceListValue_forStr(new_datatype, 'WGS', 'DNA')
    new_datatype = ReplaceListValue_forStr(new_datatype, 'RNA-Seq', 'RNA')

    dict_IDwithDataType = dict(zip(info['ID'], new_datatype))
    # ID:DataType
    
    ## 3. check samples per case
    summary_rec_per_case = CheckSampleMatching_forCase(info, df, dict_IDwithDataType, args.outdir)

    ## 4. check swap samples
    Check_sampleSwap_v2(info, df, dict_IDwithDataType, summary_rec_per_case, args.outdir)



    
'''
    Set functions
'''

## CheckDataInfo
def CheckDataInfo(info, data, path):
    info_samples = list(info['ID'].values)
    data_samples = list(data.columns.values)

    not_intersection = list(set(info_samples) ^ set(data_samples))
    
    if len(not_intersection) > 0:
        print(f'[WARNING] Please check the non-intersecting samples from no_intersection_samples.log ... total {len(not_intersection)}')
        
        with open(f'{path}/no_intersection_samples.log', 'w') as output:
            output.write('\n'.join(not_intersection))
    else:
        print('[INFO] Data & Info are matching ... ok')




## ReplaceListValue_forStr
def ReplaceListValue_forStr(strList, str_old, str_new):
    new_string_list = []

    for string in strList:
        new_string = string.replace(str_old, str_new)
        new_string_list.append(new_string)

    return new_string_list




##----------------- I. CheckSampleMatching_forCase
def CheckSampleMatching_forCase(info, data, dict_info, outdir):
    
    caseList = list(info['CaseID'].unique())
    
    summary_rec = pd.DataFrame(columns=['ID', 'Matched_DNA', 'Matched_RNA', 'Total_Matched_N', 'Matched_Rate', 'QC', 'LowCor_with'])

    for caseID in caseList:
        sampleList = list(info.loc[info['CaseID']==caseID, 'ID'])
        summary_rec = MakeSummaryReport_forCaseLevel(data, dict_info, sampleList, summary_rec)

    # output
    print('[INFO] Output germlineQC.summary.per_case.out ... ok')
    summary_rec.sort_values(by=['QC'], ascending=True, inplace=True)
    summary_rec.to_csv(f'{outdir}/report.summary_germlineQC.out', sep='\t', index=False)

    return summary_rec




## ExtractDataFromMatrix
def MakeSummaryReport_forCaseLevel(df, dict_info, sampleList, summary_rec):
    # extract target data
    df_tar = df[sampleList]
    df_tar = df_tar.loc[sampleList]

    # summary per sample from same case
    n = df_tar.shape[0]  # sample size
    colnameList = list(df_tar.columns.values)
    rownameList = list(df_tar.index.values)
    
    for i in range(0,n):
        targetID = rownameList[i]
        target_dataType = dict_info.get(targetID, 0)
        
        low_cor_id = ''
        dna_n = 0
        rna_n = 0
        for j in range(0,n):
            queryID = colnameList[j]
            if targetID == queryID:
                continue
            else:
                # add datatype
                query_dataType = dict_info.get(queryID, 0)
                cor_val = df_tar.iloc[i,j]
                
                val = EstimateCompValue(target_dataType, query_dataType, cor_val)
                if query_dataType=='DNA' and val==1:
                    dna_n = dna_n + 1
                if query_dataType=='RNA' and val==1:
                    rna_n = rna_n + 1
                if val == -1:
                    if low_cor_id:
                        low_cor_id = low_cor_id + ',' + queryID
                    else:
                        low_cor_id = queryID

        # add record per sample
        total_matched = dna_n + rna_n
        matched_rate = 0
        if n > 1 :
            matched_rate = float(format(total_matched/(n-1)*100, '.2f'))   # n-1 for removing counting itself
        
        qc = 'PASS'
        if matched_rate < 50:
            qc = 'FAIL'
        if matched_rate == 50:
            qc = 'AMBIGUITY'
        if n == 1:
            qc = 'SINGLE'
        
        rec = {'ID':targetID, 'Matched_DNA':dna_n, 'Matched_RNA':rna_n, 'Total_Matched_N':int(total_matched), 'Matched_Rate':matched_rate, 'QC':qc, 'LowCor_with':low_cor_id}
        summary_rec = summary_rec.append(rec, ignore_index=True)


    return summary_rec
                



# record matched sample info e.g. sample1 record sample2 info
# 0.6-0.68 samples may relate with swap (from WashU samples)
def EstimateCompValue(dataType1, dataType2, cor_val):
    dataType =  list(set([dataType1] + [dataType2]))

    # WES > 0.78 adjected by washU str results
    if dataType == ['DNA']:
        if cor_val > 0.78:
            return 1
        else:
            return -1
    
    # RNA > 0.68 adjected by washU distribution
    if 'RNA' in dataType:
        if cor_val > 0.68:
            return 1
        else:
            return -1
    




##----------------- II. Check_SampleSwap

def Check_sampleSwap_v2(info, data, dict_info, sample_qc_report, outdir):
    dict_case = dict(zip(info['ID'], info['CaseID']))

    # potential issue samples from same case
    issue_data = sample_qc_report.loc[sample_qc_report['QC']!='PASS', ['ID','QC']]
    potential_sample = list(issue_data['ID'].values)
    n = issue_data.shape[0]
    data_sec = data.loc[potential_sample]
    
    # report
    summary_swap = pd.DataFrame(columns=['TargetID', 'TargetCaseID', 'Status_with_targetCase', 'NewMatch', 'Matched_OtherCaseID', 'Matched_OtherID', 'Cor_withOtherID'])
    # Note: Swap/Mislabeling. It may belong to CaseID.
    N = data.shape[0]
    colnameList = list(data.columns.values)
    
    for i in range(0,n):
        targetID = potential_sample[i]
        target_dataType = dict_info.get(targetID)
        status_in_sameCase = sample_qc_report.loc[sample_qc_report['ID']==targetID, 'QC'].values[0]
        
        queryID = ''
        target_case = ''
        query_case = ''
        for j in range(0,N):
            queryID = colnameList[j]
            target_case = dict_case.get(targetID)
            query_case = dict_case.get(queryID)

            val = 0
            cor_val = 0
            if target_case != query_case :
                #cor_val = data_sec.iloc[i,j]
                cor_val = float(data_sec.loc[targetID, queryID])
                target_dataType = dict_info.get(targetID)
                query_dataType = dict_info.get(queryID)
            
                val = EstimateCompValue(target_dataType, query_dataType, cor_val)
                
                if val == 1:
                    rec = {'TargetID':targetID, 'TargetCaseID':target_case, 'Status_with_targetCase':status_in_sameCase, 'NewMatch':f'MatchToCase:{query_case}', 'Matched_OtherCaseID':query_case, 'Matched_OtherID':queryID, 'Cor_withOtherID':float(format(cor_val, '.2f'))}
                    summary_swap = summary_swap.append(rec, ignore_index=True)


    summary_swap_mean = pd.DataFrame()

    # log    
    if summary_swap.shape[0] == 0:
        print('[INFO] No swap samples ... ok')
    else:
        print('[WARNING] Detected some potential swap samples ... require to check')
        summary_swap_mean = summary_swap.groupby(['TargetID', 'TargetCaseID', 'Status_with_targetCase', 'NewMatch'])['Cor_withOtherID'].mean().reset_index(name="MeanCor_for_newMatch")

    
    
    # output
    print('[INFO] Output germlineQC.potential.swap_data.out ... ok')
    summary_swap_mean.to_csv(f'{outdir}/report.germlineQC.potential.swap_data.out', sep='\t', index=False)






if __name__ == '__main__':
    main()
    end_time = datetime.datetime.now()
    print('[INFO] Completed ... ', end_time.strftime("%Y-%m-%d %H:%M:%S"))


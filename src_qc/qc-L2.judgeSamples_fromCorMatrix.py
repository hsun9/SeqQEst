"""

    Author: Hua Sun
    Email: hua.sun@wustl.edu/hua.sun229@gmail.com
    
    11/24/2019 v0.3

    python3 qc-L2.judgeSamples_fromCorMatrix.py -i input.file -a anno.file -o outdir


    > input.file (head=T)
        # the data from "qc-L2.cor_matrix4allSamples.py"
        samples  cor
        sample1--sample2  cor_value


    > anno.file (head=T)
        CaseID  ID  NewID   DataType    Group
        WU-0012 TWDE-HPB_242-242-03 WU-0012.WES.N   WES Human_Normal
        WU-0059 TWDE-WUR-014-DRESL5C_4639   WU-0059.WES.P2  WES PDX

        DataType = WES/WXS/WGS/RNA-Seq
        Group = Human_Normal/Human_Tumor/PDX


    > output files
        1. group_byCase.pass_fail_samples.out
          
          'WES-N':Normal, 'WES-T':Tumor, 'WES-P':PDX, 'RNA-N':Normal, 'RNA-T':Tumor, 'RNA-P':PDX
            QC score: 0-NA, 1-PASS, -1-FAIL
            NOTE: The QC score will accumulation and get final sum for solving multiple samples within a same group
            If the sum value as <0 then FAIL, ==0 then Ambiguity, >0 PASS

        2. potential_swap_samples.out


"""

import argparse
import os
import pandas as pd
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", metavar="FILE", type=str, help="input matrix")
parser.add_argument("-a", "--anno", metavar="FILE", type=str, help="input matrix")
parser.add_argument("-o", "--outdir", metavar="Folder", type=str, default=os.getcwd(), help="output directory")

args = parser.parse_args()


# start time
start_time = datetime.datetime.now()
print ('[INFO] Running ... ', start_time.strftime("%Y-%m-%d %H:%M:%S"))


# make directory
path = args.outdir

try:
    if not os.path.isdir(path):
        os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)



# set global dictionary
globalDicRec = dict()
globalDicRecSwapSamples = dict()




## Function - save to dictionary for PASS
def funcSave2DircPass(sample, dataType, group):
    # DN, DT, DP, RN, RT, RP
    # 0,  1,  2,  3,  4,  5
    # print(sample, dataType, group)
    # DN
    if dataType in ['WES', 'WXS'] and group in ['human_normal', 'Human_Normal']:
        if sample in globalDicRec:
            globalDicRec[sample][0] += 1
        else:
            globalDicRec[sample] = [1, 0, 0, 0, 0, 0]
        return

    # DT
    if dataType in ['WES', 'WXS'] and group in ['human_tumor', 'Human_Tumor']:
        if sample in globalDicRec:
            globalDicRec[sample][1] += 1
        else:
            globalDicRec[sample] = [0, 1, 0, 0, 0, 0]
        return

    # DP
    if dataType in ['WES', 'WXS'] and group in ['pdx', 'PDX']:
        if sample in globalDicRec:
            globalDicRec[sample][2] += 1
        else:
            globalDicRec[sample] = [0, 0, 1, 0, 0, 0]
        return

    # RN
    if dataType == "RNA-Seq" and group in ['human_normal', 'Human_Normal']:
        if sample in globalDicRec:
            globalDicRec[sample][3] += 1
        else:
            globalDicRec[sample] = [0, 0, 0, 1, 0, 0]
        return
    # RT
    if dataType == "RNA-Seq" and group in ['human_tumor', 'Human_Tumor']:
        if sample in globalDicRec:
            globalDicRec[sample][4] += 1
        else:
            globalDicRec[sample] = [0, 0, 0, 0, 1, 0]
        return

    # RP
    if dataType == "RNA-Seq" and group in ['pdx', 'PDX']:
        if sample in globalDicRec:
            globalDicRec[sample][5] += 1
        else:
            globalDicRec[sample] = [0, 0, 0, 0, 0, 1]




## Function - save to dictionary for Fail
def funcSave2DircFail(sample, dataType, group):
    # DN, DT, DP, RN, RT, RP
    # 0,  1,  2,  3,  4,  5
    # DN
    if dataType in ['WES', 'WXS'] and group in ['human_normal', 'Human_Normal']:
        if sample in globalDicRec:
            globalDicRec[sample][0] += -1
        else:
            globalDicRec[sample] = [-1, 0, 0, 0, 0, 0]
        return

    # DT
    if dataType in ['WES', 'WXS'] and group in ['human_tumor', 'Human_Tumor']:
        if sample in globalDicRec:
            globalDicRec[sample][1] += -1
        else:
            globalDicRec[sample] = [0, -1, 0, 0, 0, 0]
        return

    # DP
    if dataType in ['WES', 'WXS'] and group in ['pdx', 'PDX']:
        if sample in globalDicRec:
            globalDicRec[sample][2] += -1
        else:
            globalDicRec[sample] = [0, 0, -1, 0, 0, 0]
        return

    # RN
    if dataType == "RNA-Seq" and group in ['human_normal', 'Human_Normal']:
        if sample in globalDicRec:
            globalDicRec[sample][3] += -1
        else:
            globalDicRec[sample] = [0, 0, 0, -1, 0, 0]
        return

    # RT
    if dataType == "RNA-Seq" and group in ['human_tumor', 'Human_Tumor']:
        if sample in globalDicRec:
            globalDicRec[sample][4] += -1
        else:
            globalDicRec[sample] = [0, 0, 0, 0, -1, 0]
        return

    # RP
    if dataType == "RNA-Seq" and group == "pdx":
        if sample in globalDicRec:
            globalDicRec[sample][5] += -1
        else:
            globalDicRec[sample] = [0, 0, 0, 0, 0, -1]




## Main
def main():
    dataCor = pd.read_csv(args.input, sep="\t")
    dataCor.columns = ["Samples", "Cor"]
    
    dataAnno = pd.read_csv(args.anno, sep="\t")
    dataAnno.columns = ["case", "sample", "newID", "dataType", "group"]
    
    # remove duplicates samples from the annotated file
    dataAnno.drop_duplicates(subset ="sample", inplace = True)

    # cor. data length
    n = len(dataCor.index)
    for i in range(0, n):
        # for i in range(0, 100):
        sampleSet = dataCor.Samples[i]
        sample1, sample2 = sampleSet.split('--')

        if sample1 == sample2:
            continue
        
        corVal = dataCor.at[i, 'Cor']

        if sample1 not in dataAnno.values:
            print(sample1 + ' does not exist in annotation file!')
            continue
        
        if sample2 not in dataAnno.values:
            print(sample2 + ' does not exist in annotation file!')
            continue


        case1 = dataAnno.loc[dataAnno['sample'] == sample1, 'case'].values[0]
        case2 = dataAnno.loc[dataAnno['sample'] == sample2, 'case'].values[0]

        group1 = dataAnno.loc[dataAnno['sample'] == sample1, 'group'].values[0]
        group2 = dataAnno.loc[dataAnno['sample'] == sample2, 'group'].values[0]

        dataType1 = dataAnno.loc[dataAnno['sample'] == sample1, 'dataType'].values[0]
        dataType2 = dataAnno.loc[dataAnno['sample'] == sample2, 'dataType'].values[0]


        # cor cutoff as 0.68
        if case1 == case2:
            # record matched sample info e.g. sample1 record sample2 info
            # 0.6-0.68 samples may relate with swap (from WashU samples)
            if dataType1 == "RNA-Seq" or dataType2 == "RNA-Seq":
                # RNA > 0.68 adjected by washU distribution
                if corVal > 0.68:
                    funcSave2DircPass(sample1, dataType2, group2)
                    funcSave2DircPass(sample2, dataType1, group1)
                else:
                    funcSave2DircFail(sample1, dataType2, group2)
                    funcSave2DircFail(sample2, dataType1, group1)
            else:
                # WES > 0.78 adjected by washU str results
                if corVal > 0.78:
                    funcSave2DircPass(sample1, dataType2, group2)
                    funcSave2DircPass(sample2, dataType1, group1)
                else:
                    funcSave2DircFail(sample1, dataType2, group2)
                    funcSave2DircFail(sample2, dataType1, group1)
        else:
            # swap sample cutoff >0.8 (learn from PDMR samples)
            if corVal > 0.8:
                swapSampleSet = sample1 + '(' + case1 + ':' + dataType1 + ':' + group1 + ')' + '--' + sample2 + '(' + case2 + ':' + dataType2 + ':' + group2 + ')'
                globalDicRecSwapSamples[swapSampleSet] = corVal





## Output results
def outputResults():
    # save pass and fail info
    if bool(globalDicRec):
        # make dataframe and add colnames
        df = pd.DataFrame.from_dict(globalDicRec, orient='index', columns=['WES-N', 'WES-T', 'WES-P', 'RNA-N', 'RNA-T', 'RNA-P'])
        # add sum col & sort by value
        df['Sum'] = df.sum(axis=1)
        df.sort_values(by=['Sum'], ascending=True, inplace=True)
        # Add a new column named 'Description'
        df['Desc'] = ['PASS' if x>0 else 'FAIL' for x in df['Sum']]
        df.loc[df.Sum == 0, 'Desc'] = 'Ambiguity'

        df.to_csv(args.outdir + '/group_byCase.pass_fail_samples.out', sep="\t", index=True, header=True)
    else:
        print("[NOTE] No results ......")
    
    # save swap sample info
    if bool(globalDicRecSwapSamples):
        df = pd.DataFrame.from_dict(globalDicRecSwapSamples, orient='index', columns=['Cor'])
        df.to_csv(args.outdir + '/potential_swap_samples.out', sep="\t", index=True, header=True)
    else:
        print("[NOTE] No swap samples ......")


    


if __name__ == '__main__':
    main()
    outputResults()
    
    end_time = datetime.datetime.now()
    print('[INFO] Completed ... ', end_time.strftime("%Y-%m-%d %H:%M:%S"))
        


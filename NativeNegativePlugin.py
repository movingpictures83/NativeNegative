import PyIO
import PyPluMA
import pickle


class NativeNegativePlugin:
    def input(self, inputfile):
       self.parameters = PyIO.readParameters(inputfile)
    def run(self):
        pass
    def output(self, outputfile):
        attnfile = open(PyPluMA.prefix()+"/"+self.parameters["attnfile"], "rb")
        attn_df_test = pickle.load(attnfile)
        score_df = attn_df_test[['PPI', 'CAPRI_quality','PIsToN_score']].drop_duplicates()
        score_df['PID'] = score_df['PPI'].apply(lambda x: x.split('-')[0] if '-' in x else x.split('_')[0])

        score_df_native = score_df[score_df[self.parameters["nativevar"]]==int(self.parameters["nativeval"])]
        score_df_native["PIsToN_native"] = score_df_native['PIsToN_score']
        score_df_native["PPI_native"] = score_df_native['PPI']
        score_df_native = score_df_native[['PPI_native', 'PID','PIsToN_native']]

        score_df_incorrect = score_df[score_df[self.parameters["incorrectvar"]]==int(self.parameters["incorrectval"])]
        score_df_incorrect = score_df[score_df['CAPRI_quality']==4]
        score_df_incorrect["PIsToN_incorrect"] = score_df_incorrect['PIsToN_score']
        score_df_incorrect["PPI_neg"] = score_df_incorrect['PPI']
        score_df_incorrect = score_df_incorrect[['PPI_neg','PID','PIsToN_incorrect']]

        score_df = score_df_native.merge(score_df_incorrect, how='left', on='PID')
        score_df['diff'] = score_df['PIsToN_incorrect'] - score_df['PIsToN_native']
        score_df = score_df.sort_values(by='diff', ascending=False)
        outfile = open(outputfile, "wb")
        pickle.dump(score_df, outfile)

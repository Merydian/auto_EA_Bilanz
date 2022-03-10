import pandas as pd
import os

class EAsummary:
    def __init__(self, dir):
        self.dir = dir
        self.data = {}
        
        self.get_data()
        self.calc()
        
    def get_data(self):
        for file in os.listdir(self.dir):
            if file.endswith('.csv'):
                path = self.dir + file
                df = pd.read_csv(path, sep=';', decimal=',')
                self.data[file] = df

        
    def calc(self):
        df1 = self.data['Eingriff_temporär.csv']
        df2 = self.data['Ausgleich_temporär.csv']
        tempGes =  df1['WPdiff'].sum() + df2['WPdiff'].sum()
        print(tempGes)
        
        df3 = self.data['Eingriff_dauerhaft.csv']
        df4 = self.data['Ausgleich_dauerhaft.csv']
        dauerhaftGes =  df3['WPdiff'].sum() + df4['WPdiff'].sum()
        
        print(dauerhaftGes)
        
dir = "C:/Users/T/Documents/GitHub/auto_EA_Bilanz/output/"
EAsummary(dir)
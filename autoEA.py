import pandas as pd
import numpy as np

class autoEA:
    def __init__(self, biotop, planung, tempVals, lastingVals, lastingName, tempName ):
        self.planung = QgsProject.instance().mapLayersByName(planung)[0]
        self.biotop = QgsProject.instance().mapLayersByName(biotop)[0]
        self.clipLayer = None
        self.lastingVals = lastingVals
        self.tempVals = tempVals
        self.lastingName = lastingName
        self.tempName = tempName
        self.LUTpath = "C:\\Users\\T\\Documents\\GitHub\\auto_EA_Bilanz\\LUT_shk.csv"
        self.outPath = "C:/Users/T/Documents/GitHub/auto_EA_Bilanz/output/"
        
        self.intersect()
        self.addArea(self.clipLayer)
        self.groupKV_typ(self.clipLayer, self.lastingVals, self.lastingName, 'Ausgleich_dauerhaft')
        self.groupKV_typ(self.clipLayer, self.tempVals, self.tempName, 'Eingriff_temporär')
        self.groupKV_typ(self.clipLayer, self.lastingVals, self.tempName, 'Eingriff_dauerhaft')
        self.groupKV_typ(self.clipLayer, self.tempVals, self.lastingName, 'Ausgleich_temporär')
        
    def intersect(self):
        
        result = processing.run('native:intersection', 
                            { 'INPUT' : self.biotop.source(),
                            'INPUT_FIELDS' : [],
                            'OUTPUT' : 'TEMPORARY_OUTPUT',
                            'OVERLAY' : self.planung.source(),
                            'OVERLAY_FIELDS' : [],
                            'OVERLAY_FIELDS_PREFIX' : '' })

        
        #self.clipLayer = QgsProject.instance().mapLayersByName('Intersection')[0]
        self.clipLayer = result['OUTPUT']

        
    def addArea(self, layer):
        
        caps = layer.dataProvider().capabilities()

        fields_name = [f.name() for f in layer.fields()]

        if caps & QgsVectorDataProvider.AddAttributes:
            if "Area" not in fields_name:
                layer.dataProvider().addAttributes([QgsField("Area", QVariant.Double)])
                layer.updateFields()
                fields_name = [f.name() for f in layer.fields()]
                fareaidx = fields_name.index('Area')
            else:
                print("The Area field is already added")
                fields_name = [f.name() for f in layer.fields()]
                fareaidx = fields_name.index('Area')


        if caps & QgsVectorDataProvider.ChangeAttributeValues:

            for feature in layer.getFeatures():
                attrs = {fareaidx : round(feature.geometry().area(), 2)}
                layer.dataProvider().changeAttributeValues({feature.id() : attrs})
    
    
    def groupKV_typ(self, lyr, spalten, spalte, name):

        cols = [f.name() for f in lyr.fields()] 
        datagen = ([f[col] for col in cols] for f in lyr.getFeatures())
        df = pd.DataFrame.from_records(data=datagen, columns=cols)

        d = df.loc[df['MASSN_TYP'].isin(spalten)]

        df = pd.pivot_table(d, values='Area', 
                                    index=[spalte], 
                                    columns=['MASSN_TYP'], 
                                    aggfunc=np.sum,
                                    fill_value=0)

        da = pd.DataFrame()
        da['totalArea'] = df.sum(axis=1)
    
        db = pd.read_csv(self.LUTpath, dtype={'Typ': str, 'WP': float}, sep=';', encoding='utf8')
        
        # check if all Vals are in LUT
        for i in d[spalte]:
            if i not in db['Typ'].tolist():
                x = i + 'Not contained in LUT'
                print('WARNING: ' + i + ' not contained in LUT\n')
        
        
        dc = da.merge(db, left_on=spalte, right_on='Typ', how='left')
        
        dc = dc[['Typ', 'Standard-Nutzungs-/Biotoptyp', '§30  ', 'Übersch.', 'WP', 'totalArea']]
        
        dc['Biotopwert'] = dc['WP'] * dc['totalArea']
        
        if 'Eingriff' in name:
            dc['WPdiff'] = dc['Biotopwert'] - 0
            
        elif 'Ausgleich' in name:
            dc['WPdiff'] = 0 - dc['Biotopwert']
        
        print(name)
        #print('\nSpaltenname: ' + spalte)
        #print('\nValues: ')
        #print(spalten)
        #print(dc[['Typ', 'WPdiff', 'totalArea']])
        #print('\nWP gesamt: ' + str(dc['WPdiff'].sum()))
        #print('\n\n\n\n')
        dc.to_csv(self.outPath + name + ".csv", encoding="utf-8", index = False, sep = ";", decimal= ",")
        

tempName = 'KV_Typ'
lastingName = 'MASSN_KV'

tempVals = ['B_Gruenflaeche', 'B_Gruenflaeche_Boeschung', 'B_Wald', 'B_Wald_Entsiegelung', 'B_Wald_Ersatzaufforstung']
lastingVals = ['A_Bach', 'A_Befestigung', 'A_Befestigung_Boeschung', 'A_Graben', 'A_Gruenflaeche_Boeschung', 'A_Versiegelung',]

Biotop = 'Cleaned'
Planung = 'L19_07_Planung'

autoEA(biotop=Biotop, planung=Planung, tempVals=tempVals, tempName=tempName, lastingVals=lastingVals, lastingName=lastingName)

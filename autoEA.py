import pandas as pd
import numpy as np

class autoEA:
    def __init__(self, biotop, planung, tempCols, lastingCols, lastingName, tempName ):
        self.planung = QgsProject.instance().mapLayersByName(planung)[0]
        self.biotop = QgsProject.instance().mapLayersByName(biotop)[0]
        self.clipLayer = None
        self.lastingCols = lastingCols
        self.tempCols = tempCols
        self.lastingName = lastingName
        self.tempName = tempName
        self.LUTpath = "C:/Users/T/Desktop/autoEA/LUT_shk.csv"
        
        self.clip()
        self.addArea(self.clipLayer)
        self.groupKV_typ(self.clipLayer, self.lastingCols, self.lastingName, 'Ausgleich dauerhaft')
        self.groupKV_typ(self.clipLayer, self.tempCols, self.tempName, 'Eingriff temporär')
        self.groupKV_typ(self.clipLayer, self.lastingCols, self.tempName, 'Eingriff dauerhaft')
        self.groupKV_typ(self.clipLayer, self.tempCols, self.lastingName, 'Ausgleich temporär')
        
    def clip(self):
        
        result = processing.runAndLoadResults('native:intersection', 
                            { 'INPUT' : self.biotop.source(),
                            'INPUT_FIELDS' : [],
                            'OUTPUT' : 'TEMPORARY_OUTPUT',
                            'OVERLAY' : self.planung.source(),
                            'OVERLAY_FIELDS' : [],
                            'OVERLAY_FIELDS_PREFIX' : '' })

        
        self.clipLayer = QgsProject.instance().mapLayersByName('Intersection')[0]
        
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

        df = df.loc[df['MASSN_TYP'].isin(spalten)]

        df = pd.pivot_table(df, values='Area', 
                                    index=[spalte], 
                                    columns=['MASSN_TYP'], 
                                    aggfunc=np.sum,
                                    fill_value=0)

        da = pd.DataFrame()
        da['totalArea'] = df.sum(axis=1)
    
        db = pd.read_csv(self.LUTpath, dtype={'Typ': str, 'WP': float}, sep=';', encoding='utf8')

        dc = da.merge(db, left_on=spalte, right_on='Typ', how='left')
        
        dc = dc[['Typ', 'Standard-Nutzungs-/Biotoptyp', '§30  ', 'Übersch.', 'WP', 'totalArea']]
        
        dc['Biotopwert'] = dc['WP'] * dc['totalArea']
        dc['WPdiff'] = dc['Biotopwert'] - 0
        
        print(db['Standard-Nutzungs-/Biotoptyp'])
        print(spalte)
        print(spalten)
        print(dc)
        print('\n\n\n\n')
        dc.to_csv("C:/Users/T/Desktop/autoEA/output/" + name + ".csv", encoding="utf-8", index = False, sep = ";", decimal= ",")
        

tempName = 'KV_Typ'
lastingName = 'MASSN_KV'

tempCols = ['B_Gruenflaeche', 'B_Gruenflaeche_Boeschung', 'B_Wald', 'B_Wald_Entsiegelung', 'B_Wald_Ersatzaufforstung']
lastingCols = ['A_Bach', 'A_Befestigung', 'A_Befestigung_Boeschung', 'A_Graben', 'A_Gruenflaeche_Boeschung', 'A_Versiegelung',]

Biotop = 'Cleaned'
Planung = 'L19_07_Planung'

autoEA(biotop=Biotop, planung=Planung, tempCols=tempCols, tempName=tempName, lastingCols=lastingCols, lastingName=lastingName)

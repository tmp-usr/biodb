import os,re
from collections import OrderedDict

from storm.locals import create_database, Store
from storm_objects import BioDB, Hierarchy



class Updater(BioDBBase):
    """
        Updater super class for fantom dbs
        db_name: database name
        fantom_db_path: path to tabular fantom input database file
        sql_db_path: path to the fantom database
    """

    def __init__(self, db_name, biodb_tmp_db_path=""):
        self.db_name= db_name
        self.biodb_tmp_db_path= biodb_tmp_db_path 
        
        BioDBBase.__init__(self, self.db_name, self.biodb_tmp_db_path)
        
    
    def update_feature_by_id(self, id, name="", accession="", level=""):
        feature= self.store.find(BioDB, BioDB.id == id).one()
        if name != "":
            feature.name = name

        if accession != "":
            feature.accession = accession

        if level != "":
            feature.level = level

        self.store.commit()
        return feature


  
trash= """
def get_raw_features(self):
        self.raw_features=[]
        with open(self.fantom_db_path) as f:
            for line in f:
                columns=line.rstrip().split('\t')
                levelCount=len(columns)/2
                feature_hierarchy=[]
                for i in range(levelCount*2)[::2]:
                    feature={}
                    columns[i]= re.sub(r'[^\x00-\x7F]+','', columns[i])
                    feature[columns[i]]=columns[i+1]
                    feature_hierarchy.append(feature)
                self.raw_features.append(feature_hierarchy)
"""

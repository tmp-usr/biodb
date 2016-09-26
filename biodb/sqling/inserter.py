import re

from collections import OrderedDict

from biodb_base import BioDBBase

from storm_objects import BioDB, Hierarchy, Lineage
from dropper import Dropper


class Inserter(BioDBBase):
    def __init__(self, db_name, tmp_db_path):
        BioDBBase.__init__(self, db_name)
        self.tmp_db_path= tmp_db_path
        
        self.exists= self.init_table()
        if self.exists:
            msg= """
            The database exists, use the updator module!
            """
            if self.db_name == "ncbi":
                print "working on the ncbi taxonomy database!"
                pass
            #self.read_and_store_features_from_tmp()
            #self.store.flush()
            #raise Exception(msg)
        
        else:
            """
            - read the temporary biodb file
            - create tables
            - insert features
            - commit
            - insert hierarchies
            - commit
            - flush
            """
            
            self.create_tables()
            self.read_and_store_features_from_tmp()
            #self.insert_features_and_hierarchies()
            #self.store.commit()
            #self.insert_hierarchies()
            #self.store.commit()
            self.store.flush()
            #del self.store


    def create_tables(self):
        self.create_biodb_string='CREATE TABLE '+ self.biodb_table +' (id INTEGER PRIMARY KEY, name VARCHAR, accession VARCHAR, level INTEGER)'

        self.create_hier_string='CREATE TABLE '+ self.hier_table +' (childID INTEGER, parentID INTEGER, PRIMARY KEY  (childID, parentID), FOREIGN KEY (childID) REFERENCES '+ self.biodb_table+'(id), FOREIGN KEY (parentID) REFERENCES '+ self.biodb_table +'(id))'

        self.create_lineage_string='CREATE TABLE '+ self.lineage_table +' (id INTEGER PRIMARY KEY, childID INTEGER, lineage VARCHAR, FOREIGN KEY (childID) REFERENCES '+ self.biodb_table+'(id))'

        self.store.execute(self.create_biodb_string)
        self.store.execute(self.create_hier_string)
        self.store.execute(self.create_lineage_string)

    def read_and_store_features_from_tmp(self):
        """
            inserts biodb features into 3 tables (biodb, hier, lineage) at
            consecutively in one go. previously employed functions, 
            insert features and insert hierarchies are eliminated. 
            Project balter is hereby suspended and merged in to biodb. 
        """

        self.raw_features=[]
        all_features= {} # key (level, name); value (id, accession)
        id=0
        line_no=0
        child_parent= {}
        with open(self.tmp_db_path) as f:
            for line in f:
                line_no += 1
                lineage_id= line_no
                columns=line.rstrip().split('\t')
                levelCount=len(columns)/2
                feature_hierarchy=[]
                
                for i in range(levelCount*2)[::2]:
                    feature= {}
                    
                    columns[i]= re.sub(r'[^\x00-\x7F]+','', columns[i])
                    
                    name= columns[i]
                    accession = columns[i+1]
                    level = (i / 2) + 1
                   
                    if (name, accession, level) in all_features:
                        id= all_features[(name, accession,level)]
                         
                    else:
                        new_id= len(all_features)+1
                        all_features[(name, accession, level)] = new_id
                        self.insert_feature(new_id, name, accession, level)
                        
                        try:
                            self.store.commit()
                        except Exception,e:
                            print e
                            pdb.set_trace()
                        
                        id = new_id
                    
                    feature= [id, name, accession, level]
                    
                    feature_hierarchy.append(feature)
               
                
                for i in range(len(feature_hierarchy)):
                    
                    child_feature= feature_hierarchy[i]
                    if child_feature[3] != 1:
                        parent_feature= feature_hierarchy[i-1]
                        if (child_feature[0], parent_feature[0]) not in child_parent:    
                            child_parent[(child_feature[0],parent_feature[0])]=1
                            self.insert_hierarchy(child_feature[0], parent_feature[0])
                        #except:
                        #    msg= """
                        #         Hierarchy exists!
                        #    """
                        #    pass

                id_hierarchy= [str(f[0]) for f in feature_hierarchy]
                #print id_hierarchy
                self.insert_lineage(lineage_id, id_hierarchy[-1], ";".join(id_hierarchy))
                #self.raw_features.append(feature_hierarchy)
        self.store.commit()


    def insert_feature(self, id, name, accession, level):
        b=BioDB()
        b.id= int(id)
        b.name = unicode(name)
        b.accession = unicode(accession)
        b.level = int(level)
        self.store.add(b)


    def insert_hierarchy(self, child_id, parent_id):
        h= Hierarchy()
        h.childID= child_id
        h.parentID= parent_id
        assert parent_id is not "", "Parent ID cannot be blank!"
        assert child_id is not "", "Parent ID cannot be blank!"
        self.store.add(h)


    
    def insert_lineage(self, id, child_id, lineage):
        l= Lineage()
        l.id= int(id)
        l.childID= int(child_id)
        l.lineage= unicode(lineage)
        self.store.add(l)

    
    def update_feature_by_id(self, id, name="", accession="", level=""):
        feature= self.store.find(BioDB, BioDB.id == id).one()
        
        if feature.level != 0:
            return 0
        
        print "Level 0 alert: %s" % feature.name 

        if name != "":
            feature.name = name

        if accession != "":
            feature.accession = accession

        if level != "":
            feature.level = level

        self.store.commit()
        return feature

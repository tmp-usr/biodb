import tarfile
from itertools import islice,chain 

from sqling.inserter import Inserter
from sqling.storm_objects import BioDB, Hierarchy
from sqling.biodb_base import BioDBBase

from paketbuiol.io_helper import BatchReader

import pdb
sep= "\t|\t"

class NoTmpUpdater(BioDBBase):
    
    def __init__(self, db_name, local_download_path):
        self.db_name= db_name
        self.local_download_path= local_download_path
        
        #BioDBBase.__init__(self, db_name)
        
        self.inserter = Inserter(db_name, local_download_path)        
    
        self.chunk_size= 10000

    def update(self):
        pass

#new_taxa_f= open('new_taxa.txt','w')

class NCBITaxonomyParserUpdater(NoTmpUpdater):
    """
        parses ncbi taxonomy database files.
    """
    def __init__(self, *args):
        NoTmpUpdater.__init__(self, *args)


        self.divisions= {0:"Bacteria",3:"Phages",9:"Viruses", 11:"Environmental samples"}
    
        self.extended_levels= ["phylum","class","order","family","genus","species","forma","infraclass","infraorder","kingdom","no rank","parvorder","species group","species subgroup","subclass","subfamily","subgenus","subkingdom","suborder","subphylum","subspecies","subtribe","superclass","superfamily","superkingdom","superorder","superphylum","tribe","varietas"]
    
    def insert_taxa(self):
        tar= tarfile.open(self.local_download_path, "r:gz")
           
        member= tar.getmember('names.dmp')
        fIn_names= tar.extractfile(member)

        tax_name= {}
        name_tax= {}
        
        br= BatchReader(self.chunk_size, iterator= fIn_names)
        acc_chunk=0
        for chunk in br:    
            for line in chunk:
                cols= line.rstrip('\n').split(sep)
               
                if cols[3].rstrip("\t|") != "scientific name":
                    continue
 

                taxid= int(cols[0])
                accession= unicode(taxid)
                ### check if taxid exists in the local database
                name= unicode(cols[1])
                level= 0#extended_levels.index(rank) +1
                
                self.inserter.insert_feature(taxid, name, accession, level)
                #if len(tax_name.keys()) == update_limit:
                #    break
            acc_chunk+= self.chunk_size
            print "Processed %i lines" % acc_chunk
    
    def insert_hier(self):
        tar= tarfile.open(self.local_download_path, "r:gz")

        member= tar.getmember('nodes.dmp')
        fIn_nodes= tar.extractfile(member)
        br= BatchReader(self.chunk_size, iterator= fIn_nodes)
        acc_chunk= 0
        
        for chunk in br:
            
            for line in chunk:
                
                cols= line.rstrip('\n').split(sep)
                division_id= int(cols[4].strip())
                rank= cols[2].strip()
                
                ##if division_id in self.divisions.keys():
                    
                taxid= childID= int(cols[0].strip())
                #name= unicode(tax_name[taxid2])
                parentID= int(cols[1].strip())
                 
                #accession= unicode(taxid)
                rank_level= self.extended_levels.index(rank) + 1
                #try:
                ##feature= self.inserter.update_feature_by_id(taxid, level = rank_level)
                ##hier_found= self.inserter.store.find(Hierarchy, (Hierarchy.childID == childID) & (Hierarchy.parentID == parentID)).one()
                
                ##if hier_found:
                ##    continue
                ##else:
                    ##self.inserter.insert_hierarchy(childID, parentID)
                #except:
                #    pass
            acc_chunk += self.chunk_size
            print "Processed %i lines" % acc_chunk


    def insert_lineage(self):
        """
           -1. delete those entries that are outside the accepted divisions
            (level == 0)
            0. create a table of ranks or a dictionary of ranks
            1. build lineages of feature (BioDB objects) from biodb.sqling.selector
            2. check if the lineages include all hierarchies from species to phylum
                if 1-6 all exists in the lineage rank:
                    - update the parentIDs for the lineages: this could be done later
                    since we will be storing the lineage hierarchy in a separate table.
                else:
                    - extract the missing ranks
                    - if missing ranks can be found in the rest of the lineage
                    with the prefixed super or sub (give priority to super) place 
                    modify the taxon name adding a super(rank) at the end in paranthesis.

            3. keep only those taxa that exist in the lineage table. delete the rest.

        """
        # step -1
        delete_string= "delete from biodb_ncbi where level == 0;"
        self.inserter.store.execute(delete_string)
        self.inserter.store.commit()
        self.inserter.store.flush()
        self.inserter.store.close()
        # step 0
        self.extended_level_dict= {k:self.extended_levels.index(k)+1 for k in self.extended_levels} 
        
        # step 1
        #self.selector.get


dmp_path= "/Users/kemal/Downloads/taxdump.tar.gz"
sql_db_path= "/Users/kemal/dbs/fantom_db/fantom.db"
db_name= "ncbi"

#tax_ids= [31971, 1485, 1177712, 1485, 712991, 29580, 305976]

tax_updater= NCBITaxonomyParserUpdater(db_name, dmp_path)
#tax_updater.insert_hier()
#tax_updater.inserter.store.flush()       

# equal names should be handled. Solved! see lines above 
# TODO!!! first level should be the division name.


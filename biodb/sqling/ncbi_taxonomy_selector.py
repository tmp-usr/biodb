from storm.locals import create_database, Store 

from biodb import biodb_sql_db_path
from storm_objects import NCBITaxonomyDivision, NCBIDivision, BioDB


class NCBITaxonomySelector(object):


    def __init__(self):
        self.__init_database()


    def __init_database(self):    
        """
        creates the sqlite database instance and checks if the database exists in biodb.
        """
        database= create_database("sqlite:%s" % biodb_sql_db_path)
        print "Created storm database from %s." % biodb_sql_db_path
        self.store= Store(database)
        

    def getTaxaByDivisionID(self, div_id):
        return self.store.find(BioDB, \
                (NCBITaxonomyDivision.taxonID == BioDB.id) & \
                (NCBITaxonomyDivision.divisionID == div_id))



    def getDivisionIDByTaxonID(self, tax_id):
        return self.store.find(NCBITaxonomyDivision, NCBITaxonomyDivision.taxonID == tax_id).one().divisionID

    def getDivisionNameByID(self, div_id):
        return self.store.find(NCBIDivision, NCBIDivision.id == div_id).one().name


n_selector= NCBITaxonomySelector()
#n_selector.getTaxaByDivisionID(0)

trash= """

f_name= "ncbi_taxonomy_lineage_types.txt"
f_out= open("division_lineage_type.txt", "w")

division_lineages= {}

with open(f_name) as f_lineages:
    for line in f_lineages:
        cols= line.rstrip("\n").split("\t")
        tax_id= cols[0]
        lin_id= cols[2]
        div_id= n_selector.getDivisionIDByTaxonID(int(tax_id))
        
        f_out.write("%d\t%s\n"%(div_id, lin_id))

f_out.close()
"""

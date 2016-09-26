from storm.locals import create_database, Store
from storm_objects import NCBITaxonomyDivision, NCBIDivision
from biodb import biodb_sql_db_path


sep= "\t|\t"


class NCBITaxnomyInserter(object):
    
    def __init__(self, divisions_file_path, taxonomy_divisions_file_path):       
        
        self.included_divisions= {0:"Bacteria",3:"Phages",9:"Viruses", 11:"Environmental samples", 
                1:"Invertebrates", 4:"Plants and Fungi"}

        self.divisions_file_path= divisions_file_path
        self.taxonomy_divisions_file_path= taxonomy_divisions_file_path
        self.__init_database()
        
        if not self.init_tables():
            self.create_tables()
        


    def __init_database(self):    
        """
        creates the sqlite database instance and checks if the database exists in biodb.
        """
        database= create_database("sqlite:%s" % biodb_sql_db_path)
        print "Created storm database from %s." % biodb_sql_db_path
        self.store= Store(database)
        

    def init_tables(self):
        self.biodb_table= "biodb_ncbi"
        self.taxonomy_division_table = "biodb_ncbi_taxonomy_division"
        self.division_table= "biodb_ncbi_division"
      
        #### check if the db_name exists in the database
        table_list= [table[0] for table in self.store.execute('select tbl_name from SQLITE_MASTER')]
       
        return 0 if self.taxonomy_division_table not in table_list else 1 


    def create_tables(self):
        self.create_taxonomy_division_string='CREATE TABLE '+ self.taxonomy_division_table +' (taxonID INTEGER PRIMARY KEY, divisionID INTEGER, FOREIGN KEY (taxonID) REFERENCES '+ self.biodb_table+'(id), FOREIGN KEY (divisionID) REFERENCES '+ self.division_table +'(id) )'
        

        self.create_division_string='CREATE TABLE '+ self.division_table +' (id INTEGER PRIMARY KEY, name VARCHAR)'


        self.store.execute(self.create_taxonomy_division_string)
        self.store.execute(self.create_division_string)

    def insert_division(self, div_id, name):
        div= NCBIDivision()
        div.id = int(div_id)
        div.name= unicode(name)

        self.store.add(div)


    def insert_taxonomy_division(self, taxon_id, div_id):
        n_tax_div= NCBITaxonomyDivision()
        n_tax_div.taxonID= int(taxon_id)
        n_tax_div.divisionID= int(div_id)

        self.store.add(n_tax_div)


    def insert_divisions_from_file(self):
        with open(self.divisions_file_path) as div_file:
            for line in div_file:
                cols= line.rstrip('\n').split(sep)
                div_id= cols[0]
                name= cols[2]
                self.insert_division(div_id, name)

        self.store.commit()

    def insert_taxonomy_divisions_from_file(self):
        i=0
        with open(self.taxonomy_divisions_file_path) as tax_div_file:
            for line in tax_div_file:
                cols= line.rstrip('\n').split(sep)
                
                division_id= int(cols[4].strip())
                
                if division_id in self.included_divisions:
                    tax_id= cols[0].strip()
                    self.insert_taxonomy_division(tax_id, division_id)

                    self.store.commit()

                    i+=1
                    if i % 10000 == 0:
                        print "%d taxa inserted!" %i 
                       

        
divisions_file= "/Users/kemal/Downloads/taxdump/division.dmp"                
nodes_file= "/Users/kemal/Downloads/taxdump/nodes.dmp"


nt_inserter = NCBITaxnomyInserter(divisions_file, nodes_file)
nt_inserter.insert_taxonomy_divisions_from_file()

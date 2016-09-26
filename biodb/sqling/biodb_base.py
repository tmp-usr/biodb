from storm.locals import create_database, Store
from storm_objects import BioDB, Hierarchy, Lineage

from biodb import biodb_sql_db_path


class BioDBBase(object):
    def __init__(self, db_name, sql_db_path= ""):       
        self.db_name= db_name
        if sql_db_path != "":
            self.biodb_sql_db_path = sql_db_path

        else:
            self.biodb_sql_db_path = biodb_sql_db_path


        self.__init_database()


    def __init_database(self):    
        """
        creates the sqlite database instance and checks if the database exists in biodb.
        """
        database= create_database("sqlite:%s" % self.biodb_sql_db_path)
        print "Created storm database from %s." % self.biodb_sql_db_path
        self.store= Store(database)
        

    def init_table(self):
        self.biodb_table = "biodb_" + self.db_name
        self.hier_table= "hier_"+ self.db_name
        self.lineage_table= "lineage_"+ self.db_name
      
        BioDB.__storm_table__ = self.biodb_table
        Hierarchy.__storm_table__ = self.hier_table
        Lineage.__storm_table__ = self.lineage_table
        #### check if the db_name exists in the database
        table_list= [table[0] for table in self.store.execute('select tbl_name from SQLITE_MASTER')]
       
        return 0 if self.biodb_table not in table_list else 1 
            #msg= "Entered biological database \"%s\" does not exist in the current version of biodb packacage!" % db_name
            #print msg
            #raise Exception(msg)




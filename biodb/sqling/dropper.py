from biodb_base import BioDBBase

class Dropper(BioDBBase):
    def __init__(self, db_name):
        BioDBBase.__init__(self, db_name)
        self.table_names= ["%s_%s" %(prefix, db_name) for prefix in ("biodb", "hier", "lineage")]
    
    def drop_tables(self):
        for drop_table_string in self.get_drop_table_strings():
            self.store.execute(drop_table_string)    
            self.store.commit()
        self.store.flush()

    def get_drop_table_strings(self):
        drop_table_string = "drop table "
        for table_name in self.table_names: 
            yield drop_table_string + table_name


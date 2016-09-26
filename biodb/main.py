import shutil
import os

import wget

from biodb.parsing.parser import Parser
from biodb.downloading.manager import Manager
from biodb.sqling.updater import Updater
from biodb.sqling.selector import Selector

from biodb import db_tmp_dir, all_db_urls, download_dir, sql_db_path

class Main:
    def __init__(self, db_name, protocol="http", source=""):

        self.db_name= db_name
        db_tmp_path= os.path.join(db_tmp_dir, '%s.txt' % db_name)
        
        urls= all_db_urls[db_name]

        self.download_manager= Manager(db_name, download_dir, protocol, urls)
        self.parser = Parser(db_name, db_tmp_path, self.download_manager, source)
        self.updater= Updater(db_name, sql_db_path, db_tmp_path )
   

    def run(self):
        print "Downloading the database..."
        self.download_manager.download()
        print "Parsing files..."
        self.parser.parse()
        print "Updating sqlite database..."
        self.updater.store_database()
       

    def stats(self):
        self.n_ids=""
        self.n_levels=""


dbu= Main('kegg_orthology')
dbu.run()

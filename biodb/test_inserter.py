import os, glob

from sqling.inserter import Inserter
from sqling.dropper import Dropper

tmp_dir_path= "/Users/kemal/shared/repos/dev/biodb/biodb/data/tmp/"
db_paths= glob.glob(os.path.join(tmp_dir_path,"*.txt"))

#for db_path in db_paths:
#db_name= os.path.basename(db_path).rstrip(".txt")
db_name= "tigrfams"
db_path= os.path.join(tmp_dir_path, "%s.txt" %db_name)

try:
    Dropper(db_name).drop_tables()
except:
    pass
Inserter(db_name, db_path)



#mock_db_name= "kegg_mock"


#inserter= Inserter(mock_db_name, mock_tmp_path)






from biodb.sqling.updater import Updater
sql_db_path= "../data/db/pacfm.db"
tmp_path= "../data/tmp/kegg_orthology_metabolism.txt"
upd= Updater('kegg_orthology_metabolism', sql_db_path, tmp_path)
upd.store_database()

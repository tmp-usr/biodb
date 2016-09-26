import os, sys

#def resource_path(relative):
#    if hasattr(sys, "_MEIPASS"):
#        return os.path.join(sys._MEIPASS, relative)
#    return os.path.join(relative)


def resource_path(relative):
    if getattr(sys, 'frozen', False):
        return  os.path.join(sys._MEIPASS, os.path.dirname(os.path.abspath(__file__)) , relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)   


data_dir= resource_path("data")
download_dir= os.path.join(data_dir, "downloaded/")
db_tmp_dir=  os.path.join(data_dir, "tmp/") 
biodb_sql_db_path= os.path.join(data_dir, "db/pacfm.db")

all_db_urls= { 
        
        "cog": 
        {
            "default": "ftp://ftp.ncbi.nih.gov/pub/COG/COG2014/data/cognames2003-2014.tab" ,
            "functions": "ftp://ftp.ncbi.nih.gov/pub/COG/COG2014/data/fun2003-2014.tab"
        }, 

        "cog_mock": 
        {
            "default": "ftp://ftp.ncbi.nih.gov/pub/COG/COG2014/data/cognames2003-2014.tab" ,
            "functions": "ftp://ftp.ncbi.nih.gov/pub/COG/COG2014/data/fun2003-2014.tab"
        }, 

        "kegg_orthology":
        {
            "default":"http://www.genome.jp/kegg-bin/download_htext?htext=ko00001.keg&format=htext"
        },
    
        
        "kegg_modules": 
        {
            "default": "http://www.genome.jp/kegg-bin/download_htext?htext=ko00002.keg&format=htext"
        },

        "pfam":
        {
            "default":"ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.clans.tsv.gz"
        },
        
        "tigrfams":
        {
            "default":"ftp://ftp.jcvi.org/pub/data/TIGRFAMs/TIGRFAMs_15.0_INFO.tar.gz",
            "role_name":"ftp://ftp.jcvi.org/pub/data/TIGRFAMs/TIGR_ROLE_NAMES",
            "role_link":"ftp://ftp.jcvi.org/pub/data/TIGRFAMs/TIGRFAMS_ROLE_LINK"

        },

        "ncbi_taxonomy": {
            "default":"ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz",
            },
        
        "silva": {},
        "green_genes": {}


     }







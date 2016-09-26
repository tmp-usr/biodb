from collections import OrderedDict
import gzip
import tarfile

class Parser(object):

    def __init__(self, db_name, fantom_db_path, download_manager, source):
        self.db_name= db_name
        self.fantom_db_path= fantom_db_path
        self.source= source
        self.download_manager= download_manager

        self.error_message= "Download manager and parser databases are not the same!!!"

    def parse_kegg_orthology(self):
        logger= self.download_manager.get_logger('default')
        with open(logger.local_path) as fIn:
            with open(self.fantom_db_path, 'w') as fOut:
                if self.source == "m5nr":
                    for line in fIn:
                        # example line: ['KEGG Orthology (KO)', 'Human Diseases', 'Infectious Diseases', '05143 African trypanosomiasis [PATH:ko05143]', 'PLCB; phospholipase C, beta [EC:3.1.4.11]', 'K02677\n']                        
                        cols= line.rstrip('\n').split('\t')
                        pathway= cols[3].split(' ')
                        pathway_accession= "ko"+pathway[0]
                        pathway_name= " ".join(pathway[1:])
                        db_cols= [cols[1],"", cols[2], "", pathway_name, pathway_accession, cols[4], cols[5]]
                        fOut.write("\t".join(db_cols)+'\n')
                elif self.source == "":
                    k= ['A','B','C','D']
                    Line= OrderedDict.fromkeys(k)
                    for line in fIn:            
                        name=""
                        if line.startswith('A'):
                            name=line.lstrip('A').strip()
                            name= name.rstrip('</b>').lstrip('<b>')
                            Line['A']='%s\t'% name
                        
                        elif line.startswith('B'):
                            name=line.lstrip('B').strip()
                            name= name.rstrip('</b>').lstrip('<b>')
                            Line['B']='%s\t'% name
                        
                        elif line.startswith('C'):
                            cols=line.lstrip('C').strip().split()
                            name= cols[0] 
                            Line['C']= '\t'.join([' '.join(cols[1:]),cols[0]])
                        
                        elif line.startswith('D'):
                            cols=line.lstrip('D').strip().split()
                            name= cols[0] 
                            Line['D']= '\t'.join([' '.join(cols[1:]),cols[0]])
                        
                        if name == '':
                            continue

                        if None in Line.values():
                            continue
                        else:
                            fOut.write('\t'.join(Line.values()) + '\n')    
            

    def parse_kegg_modules(self):
        logger= self.download_manager.get_logger('default')
        k= ['A','B','C','D','E']
        Line= OrderedDict.fromkeys(k)
        with open(logger.local_path) as fIn:
            with open(self.fantom_db_path, 'w') as fOut:
                for line in fIn:
                    name=""
                    if line.startswith('A'):
                        name=line.lstrip('A').strip()
                        name= name.rstrip('</b>').lstrip('<b>')
                        Line['A']='%s\t'% name
                    elif line.startswith('B'):
                        name=line.lstrip('B').strip()
                        name= name.rstrip('</b>').lstrip('<b>')
                        Line['B']='%s\t'% name
                    elif line.startswith('C'):
                        name= line.lstrip('C').strip()
                        Line['C']='%s\t' % name
                    elif line.startswith('D'):
                        cols=line.lstrip('D').strip().split()
                        name= cols[0] 
                        Line['D']= '\t'.join([' '.join(cols[1:]),cols[0]])
                    elif line.startswith('E'):
                        cols=line.lstrip('E').strip().split()
                        name= cols[0]
                        if name.startswith('M'):
                            continue
                        Line['E']= '\t'.join([' '.join(cols[1:]),cols[0]])

                    if name == '':
                        continue

                    if None in Line.values():
                        continue
                    
                    else:
                        fOut.write('\t'.join(Line.values()) +'\n')     


    def parse_cog(self):
        logger_fun= self.download_manager.get_logger('functions')
            
        functions= {}
        with open(logger_fun.local_path) as fIn:
            fIn.next()
            for line in fIn:
                cols= line.rstrip('\n').split('\t')
                functions[cols[0].strip()] = cols[1]
        logger_default= self.download_manager.get_logger('default')       
        with open(logger_default.local_path) as fIn:
            with open(self.fantom_db_path, 'w') as fOut:
                fIn.next()
                for line in fIn:
                    cols= line.rstrip('\n').split('\t')
                    accession= cols[0].strip()
                    name= cols[2].strip()
                    pathway_accession= cols[1].strip()
                    if len(pathway_accession) > 1:
                        for p_accession in pathway_accession:
                            pathway_name= functions[p_accession]
                            fields= [pathway_name, p_accession, name, accession]  
                            cog_line= '\t'.join(fields) +'\n'
                            fOut.write(cog_line)
                    else:

                        pathway_name= functions[pathway_accession]
                        fields= [pathway_name, pathway_accession, name, accession]  
                        cog_line= '\t'.join(fields) +'\n'
                        fOut.write(cog_line)


    def parse_pfam(self):
        """fields in default file: Pfam accession", "clan accession", "clan ID", "Pfam ID", "Pfam description."""
        logger= self.download_manager.get_logger('default')
        with gzip.open(logger.local_path) as fIn:
            with open(self.fantom_db_path, 'w') as fOut:
                for line in fIn:
                    cols= line.rstrip('\n').split('\t')
                    fields= [cols[1], cols[2], cols[4], cols[0]]
                    pfam_line= '\t'.join(fields)+'\n'
                    fOut.write(pfam_line)
    
    def parse_tigrfams(self):
        """
            default file example:
                ID  Gpos_C8_like
                AC  TIGR04450
                DE  putative immunity protein/bacteriocin
                AU  Haft DH
                TC  27.00 27.00
                NC  25.00 25.00
                AL  clustalw_manual
                IT  subfamily
                EN  putative immunity protein/bacteriocin
                TP  TIGRFAMs
                CC  This model describes full-length proteins of Gram-positive bacteria that consist of an N-terminal signal peptide, a central region of unknown function, and a Cys-rich C-terminal region. In both the overall architecture and the apparent weak homology of the C-terminal region itself, these proteins resemble archaeal proteins such as the halocin C8 precursor. In that precursor, the C-terminal region is a bacteriocin but the N-terminal region functions as the immunity protein. The related family of halocin C8-like bacteriocins and their bacterial homologs are recognized by model TIGR04449
            
            role_name line example:
                
                role_id:	100	mainrole:	Central intermediary metabolism
                role_id:	100	sub1role:	Amino sugars
            
            role_link line_example:
                TIGR00001	158

        """

        logger_default= self.download_manager.get_logger('default')
        logger_role_name= self.download_manager.get_logger('role_name')
        logger_role_link= self.download_manager.get_logger('role_link')
        
        accession_desc={}
        tar= tarfile.open(logger_default.local_path, "r:gz")
        
        for member in tar.getmembers():
            fIn= tar.extractfile(member)
            content= fIn.read()
            fields= content.split('\n')
            for field in fields:
                if field.startswith('AC'):
                    acc= field.split()[1]
                elif field.startswith('DE'):
                    desc= field.split()[1]
                    accession_desc[acc]= desc
                continue
        tar.close()

        main_sub={}

        with open(logger_role_name.local_path) as fIn:
            for line in fIn:
                main_line= line
                cols_main= main_line.rstrip('\n').split('\t')
                sub_line= fIn.next()
                cols_sub= sub_line.rstrip('\n').split('\t')
                if cols_main[3] not in main_sub:
                    main_sub[cols_main[3]]={}
                if cols_sub[1] not in main_sub[cols_main[3]]:
                    main_sub[cols_main[3]][cols_sub[1]]=cols_sub[3]

        with open(logger_role_link.local_path) as fIn:
            with open(self.fantom_db_path, "w") as fOut: 
                for line in fIn:
                    cols= line.rstrip('\n').split('\t')
                    tigr_accession= cols[0]
                    sub_acc= cols[1]
                    for k,v in main_sub.iteritems():
                        if sub_acc in v:
                            fields= [k,"",v[sub_acc], sub_acc, accession_desc[tigr_accession], tigr_accession]
                            tigr_line= "\t".join(fields)+ "\n"
                            fOut.write(tigr_line)
                        continue
            

    def parse_ncbi_taxonomy(self):
        logger_default= self.download_manager.get_logger('default')


    def parse(self):
        assert self.db_name == self.download_manager.db_name, self.error_message 
        ### functional databases
        
        if self.db_name == "kegg_orthology":
            self.parse_kegg_orthology()


        elif self.db_name == "kegg_modules":
            self.parse_kegg_modules()

        elif self.db_name == "cog":
            self.parse_cog()


        elif self.db_name == "pfam":
            self.parse_pfam()
        
        elif self.db_name == "tigrfams":
            self.parse_tigrfams()

                
        ### taxonomy databases

        elif self.db_name == "silva":
            pass
    
        elif self.db_name == "green_genes":
            pass
        
        elif self.db_name == "ncbi_taxonomy":
            pass


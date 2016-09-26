import copy as cp
from lineage import Hierarchy, BioDB 
from biodb.sqling.storm_objects import NCBIHierUpdate, NCBITaxonUpdate
import logging
import time

import pdb

extended_levels= ["phylum", "class", "order", "family",
                  "genus", "species", "forma", "infraclass",
                  "infraorder", "kingdom", "no rank",
                  "parvorder", "species group", "species subgroup",
                  "subclass", "subfamily", "subgenus", "subkingdom",
                  "suborder", "subphylum", "subspecies", "subtribe",
                  "superclass", "superfamily", "superkingdom",
                  "superorder", "superphylum", "tribe", "varietas"]



#### WRITE the loggers and get done with this!!!!


class LineagePruner(object):
    """
        hc: hierarchy change
        nc: name change 
        nco: name change old
        ncn: name change new
    """


    def __init__(self, lineage, raw_lineage_type):
        self.lineage= lineage
        self.raw_lineage_type= raw_lineage_type

        self.set_logger()

        self.init_tables()


    
    def create_tables(self):
        hus= self.create_hier_update_string='CREATE TABLE '+ self.hier_update_table +' (taxonID INTEGER PRIMARY KEY, oldParentID INTEGER, newParentID INTEGER, FOREIGN KEY(taxonID) REFERENCES ' + self.biodb_table  +'(id), FOREIGN KEY(oldParentID) REFERENCES '+ self.biodb_table +'(id), FOREIGN KEY(newParentID) REFERENCES '+ self.biodb_table +'(id))'


        tus= self.create_taxon_update_string= 'CREATE TABLE '+ self.taxon_update_table +' (taxonID INTEGER PRIMARY KEY, oldName VARCHAR, newName VARCHAR, oldLevel INTEGER, newLevel INTEGER, FOREIGN KEY (taxonID) REFERENCES ' + self.biodb_table  +'(id))'

        for us in (hus, tus):
            self.lineage.biodb_selector.store.execute(us)


    def init_tables(self):
        

        self.store= self.lineage.biodb_selector.store


        self.hier_update_table= NCBIHierUpdate.__storm_table__
        self.taxon_update_table= NCBITaxonUpdate.__storm_table__
        self.biodb_table= BioDB.__storm_table__


        table_list= [table[0] for table in self.store.execute('select tbl_name from SQLITE_MASTER')]
        
        if not self.hier_update_table in table_list:
            self.create_tables() 
        


    def set_logger(self):
        self.logger = logging.getLogger("dev.lineage_pruner.LineagePruner")
        
        self.logger.setLevel(logging.ERROR)

    
    def prune_unnecessary(self):
        self.logger.error("## 2")
        #self.logger.error((self.lineage.leaf_taxon.name, self.lineage.taxon_list[-1].taxon.name)) 
        ids_before= [str(t.taxon.id) for t in self.lineage.taxon_list]

        
        self.logger.error(";".join(ids_before))
        
        
        self.prune_unnecessary_taxa(self.lineage.unnecessary_list)
        
        #for level in reversed(self.lineage.default_levels):
        #    if use:
        #        tax, unn= self.lineage.get_closest_unnecessary_by_level(level)
        #        self._update_unnecessary(tax, unn, level)
            
            #self._prune_unnecessary_by_level(level)
        
        
        
        ## uncomment the below line
        self._update_hierarchy()

        ids_after  = [str(t.taxon.id) for t in self.lineage.taxon_list]      
        self.logger.error(";".join(ids_after))

    def use_unnecessary_and_prune(self):
        
        self.logger.error("## 3")
        all_ids_before= [str(t.taxon.id) for t in self.lineage.taxon_list]
        
        #names_before = [t.taxon.name for t in self.lineage.taxon_list]
        self.logger.error(";".join(all_ids_before))
        #self.logger.error(";".join(names_before))
        try:
            self.replace_required()
        except:
            return 0
        
        self.prune_unnecessary_taxa(self.lineage.unnecessary_list)
    
        self._update_hierarchy()
        

        #names_after = [t.taxon.name for t in self.lineage.taxon_list]
        all_ids_after= [str(t.taxon.id) for t in self.lineage.taxon_list]

    #    self.logger.error(self.raw_lineage_type)

    #    self.logger.error(";".join(names_after))
        self.logger.error(";".join(all_ids_after))

            

        #self.replace_required2()

        #except ValueError:
        #    pass
            #pdb.set_trace()

        #except Exception,e:
        #    print e
        #    pdb.set_trace()

    def _update_hierarchy(self):
        """
            TODO!!! requires the logging methods!!!

            this method accepts only the final taxon list
            where all we need to check if the consecutive
            taxa has a child-parent relationship. if not
            set the relationshp.

        """
        
        if sorted([tax.level for tax in self.lineage.taxon_list]) != sorted(self.lineage.default_levels):
            """
                because of the previous changes, some taxa show up at the same hierarchy level as the others. we need to detect those taxa and remove from and existing clean lineage. 

            """ 
            pass
            #pdb.set_trace()
            #raise ValueError("Required taxonomic levels are not satisfied yet.")


        for i in range(len(self.lineage.taxon_list)-1):
            child_tax= self.lineage.taxon_list[i]
            parent_tax= self.lineage.taxon_list[i+1]
            
            child_id= child_tax.taxon.id
            #try:
            #try:
            hier= self.store.find(Hierarchy, Hierarchy.childID == child_id).one()
            #except:
            #    pdb.set_trace()



            if hier.parent.id != parent_tax.taxon.id:
                new_hier= Hierarchy()
                new_hier.parentID= parent_tax.taxon.id
                new_hier.childID= child_tax.taxon.id

                child_id= child_tax.taxon.id
                old_parent_id= hier.parentID
                new_parent_id= parent_tax.taxon.id
                
                nhu= NCBIHierUpdate()
                nhu.taxonID= child_id
                nhu.oldParentID= old_parent_id
                nhu.newParentID= new_parent_id

                self.store.add(nhu)

                self.store.remove(hier) 
                self.store.add(new_hier)

                self.logger.error("hc:"+';'.join(map(str, (child_id, old_parent_id, new_parent_id))))
                ### DONT FORGET TO COMMIT

                self.store.commit()
        #print "##### passss"
    
    def prune_unnecessary_taxa(self, unna):
        taxa= [self.lineage.get_taxon(unn) for unn in unna]
        
        if taxa !=  []:
            self.logger.info("Leaf: %s" %self.lineage.leaf_taxon.name)
            self.logger.info(taxa)
            self.logger.info("#####")
        
        self.lineage.taxon_list= [tax for tax in self.lineage.taxon_list if tax not in taxa]
        self.lineage.unnecessary_list= [unn for unn in self.lineage.unnecessary_list if unn not in unna]
    


    def replace_required(self):      
        """
            there should be added another diagnostic level for the lineage types to apply this function
            this is a less severe case than finding only "no rank" taxa among the unnecesssary taxa
            in the lineage. 

        """
        #for taxon in mock_tax
        #lineage= self.getTaxonomy(self.getFeatureByID(4049))
        #lineage= getTaxonomy(feature)
        #print "unn", self.lineage.unnecessary_levels
        #print "req", self.lineage.required_levels
        #print "exist", self.lineage.existing_levels
       
        if len(self.lineage.required_levels) > len(self.lineage.unnecessary_levels):
            raise ValueError("KILL ME!")

        
        all_level_names = [extended_levels[t.level-1] for t in self.lineage.taxon_list]    
        all_levels= [t.level for t in self.lineage.taxon_list]

        prefix = ""
        for req_level in self.lineage.required_levels:
            req_level_name = extended_levels[req_level -1]
            ### super_rank
            
            
            if "super%s"%req_level_name in all_level_names: 
                ### super finding alert!!!
                ### here we perform update operations
                ### the previous parentIDs will be changed
                prefix = "super"

            elif "sub%s"%req_level_name in all_level_names:
                prefix = "sub"

            #elif "no rank" in all_level_names:
            #    prefix= "no rank "
            
            if prefix != "":

                for level in self.lineage.unnecessary_levels:
                    new_rank= "%s%s" % (prefix, req_level_name)
                    if extended_levels[level -1] == new_rank:
                        ### our beloved feature
                        ### change both the name and level of this
                        ### feature. add (prefix + rankname) to the 
                        ### name.
                        
                        tax_upd= self.lineage.get_taxa_by_level(level)[0]
                       
                        self.logger.error("nco:"+";".join(map(str, (tax_upd.taxon.id, tax_upd.taxon.name, tax_upd.taxon.level))))
                        
                        old_level= tax_upd.taxon.level
                        old_name= tax_upd.taxon.name
                        
                        new_level= tax_upd.level  = tax_upd.taxon.level= req_level
                        upd_level_name= extended_levels[tax_upd.taxon.level -1]
                        tax_upd.taxon.name = "%s (%s)" % (tax_upd.taxon.name, upd_level_name)


                        ntu= NCBITaxonUpdate()
                        ntu.taxonID= tax_upd.taxon.id
                        ntu.oldName= unicode(old_name)
                        ntu.newName= unicode(tax_upd.taxon.name)
                        ntu.oldLevel= old_level
                        ntu.newLevel= new_level

                        self.store.add(ntu)
                        
                        self.logger.error("ncn:"+";".join(map(str, (tax_upd.taxon.id, tax_upd.taxon.name, tax_upd.taxon.level))))


            else:
                ##### unrank case
                
                taxa= self.lineage.get_closest_taxa_by_level(req_level, self.lineage.existing_list)
            
                #print req_level, taxa

                if len(taxa) == 2:

                    unn_to_be_used= self.lineage.taxon_list[taxa[1].index +1 : taxa[0].index]
                    
                else:
                    
                    if req_level == 1:
                        unn_to_be_used= self.lineage.taxon_list[taxa[0].index +1:]

                    elif req_level == 6:
                        unn_to_be_used= self.lineage.taxon_list[:taxa[0].index]
                    
                tax_upd= unn_to_be_used[0]
                self.logger.error("nco:"+";".join(map(str, (tax_upd.taxon.id, tax_upd.taxon.name, tax_upd.taxon.level))))
                
                old_level= tax_upd.taxon.level = tax_upd.level = req_level
                old_name= tax_upd.taxon.name
                
                upd_level_name= extended_levels[tax_upd.taxon.level -1]
                new_name= tax_upd.taxon.name = "%s (%s)" %(tax_upd.taxon.name, upd_level_name)
                new_level= tax_upd.taxon.level = tax_upd.level = req_level
                self.logger.error("ncn:"+";".join(map(str, (tax_upd.taxon.id, tax_upd.taxon.name, tax_upd.taxon.level))))
                
                
                #####
                ntu= NCBITaxonUpdate()
                ntu.taxonID= tax_upd.taxon.id
                ntu.oldName= old_name
                ntu.newName= tax_upd.taxon.name
                ntu.oldLevel= old_level
                ntu.newLevel= new_level
                #####
                
                self.store.add(ntu)

            try:
                ##### this happens when the required lineage levels
                ### are not satisfied although there are enough number of taxa to be 
                ### placed instead of required ones but located in different indexes
                ### than the required indexes.
                
                ### We should ideally change this beforehand at the 
                ### required_level check phase above. 

                self.prune_unnecessary_by_level(req_level)
        
            except:
                pass
                #pdb.set_trace()


        self.lineage.update_unnecessary()
                        
            ### Commit
            ### Update the hierarchy afterwards!


 
    def prune_unnecessary_by_level(self, level):
        """
        prunes the unnecessary taxa between the inquired level rank and its parent.
        """
       
        if level != 1:
           
            taxon_level_child= self.lineage.get_taxa_by_level(level)[0]
            taxon_level_parent= self.lineage.get_taxa_by_level(level-1)[0]

            
            index_child= self.lineage.taxon_list.index(taxon_level_child)
            index_parent= self.lineage.taxon_list.index(taxon_level_parent)
            
            
            unn_count= (index_parent - index_child) -1
            
            if unn_count:
                #self.logger.info("Number of unnecessary taxa to be pruned: %d" %unn_count)
                #self.logger.info(taxon_level_child)
                #self.logger.info(taxon_level_parent)
                unn_to_be_pruned= self.lineage.taxon_list[index_child+1: index_parent]
                
                #self.logger.info(unn_to_be_pruned)
                self.prune_unnecessary_taxa(unn_to_be_pruned)

                #self.logger.info("####")
                    #self.lineage.taxon_list.remove(tax)
                    #self.lineage.unnecessary_list.remove(tax)
        
        
        else:
            ### check how to remove items from an
            ### array within a loop. python does not
            ### allow us to remove all items by looping.
            if self.lineage.level_exists(level):
                taxon= self.lineage.get_taxa_by_level(level)[0]
                unn_to_be_pruned=[] 
                if level == 1:
                    
                    for unn in self.lineage.unnecessary_list:
                        if unn.index > taxon.index:
                            unn_to_be_pruned.append(unn)
                   

               #     if unn_to_be_pruned != []:
                        #self.logger.error(level)
                        #self.logger.error([t.level for t in self.lineage.taxon_list])
                        #self.logger.error(unn_to_be_pruned)


                    #self.logger.info(unn_to_be_pruned)
                    #self.logger.info("####")               
                            
                #elif level == 6:
                    
                #    for unn in self.lineage.unnecessary_list:
                #        if unn.index > taxon.index:
                #            unn_to_be_pruned.append(unn)
                



                self.prune_unnecessary_taxa(unn_to_be_pruned)
                        




trash = """

            
                              

    def prune_consecutive_and_set_hierarchy(feature):
        
        '''
            TODO: to be checked
            prunes the ranks above 6. when those taxa are in consecutive order
            this function sets the parent of the child taxon to the first defaut taxon
            found after the different ones.            
            prune only the ranks > 6.
        '''    
        
        ranks= [f.level for f in self.lineage.taxon_list]

        found_ranks= set(ranks).intersection(set(range(1,7)))
        different_ranks= set(ranks).difference(set(range(1,7)))


        for k, g in groupby(enumerate(different_ranks), lambda (i, x): i+x):
            g=[i for i in g]
            list_ranks= map(itemgetter(1), g)

            first_rank= list_ranks[0]
            last_rank= list_ranks[-1]

            first_index= ranks.index(first_rank)
            last_index= ranks.index(last_rank)

            child_taxon= lineage[first_index -1]
            parent_taxon= lineage[last_index +1]

            hier= s.store.find(Hierarchy, Hierarchy.childID == \
                               child_taxon.id ).one()
            hier.parentID= parent_taxon.id
        
        return self.lineage.get_lineage_from_biodb(feature)
            #self.store.commit()

"""

trash2= """

    def prune_unnecessary_taxon(self, tax, unn):
        self.lineage.taxon_list.remove(tax)
        self.lineage.unnecessary_list.remove(unn)


                     
    def update_unnecessary(self, tax, unn_tax, level):
        tax.level = level
        self.lineage.unnecessary_list.remove(unn_tax)





    def prune_unranked_and_set_hierarchy(self):
        '''
            TODO: to be checked
        '''
        #lineage= getTaxonomy(feature)
        ranks= [f.level for f in self.lineage.taxon_list]
        
        if 11 in ranks:
            for k, g in groupby(enumerate(ranks), lambda (i, x): x > 6):
                g=[i for i in g]
                list_ranks= map(itemgetter(1), g)
                list_indices= map(itemgetter(0), g)
                if 11 in list_ranks:
                    child_index = list_indices[0] - 1
                    parent_index = list_indices[-1] + 1

                    child_taxon= lineage[child_index]
                    parent_taxon= lineage[parent_index]

                    hier= s.store.find(Hierarchy, Hierarchy.childID == \
                                       child_taxon.id ).one()

                    hier.parentID= parent_taxon.id
        
        return self.lineage.get_lineage_from_biodb(feature)






"""

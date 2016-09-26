import copy as cp
from lineage import Hierarchy, BioDB
import logging


class LineagePruner(object):
    
    def __init__(self, lineage):
        self.lineage= lineage
        #self.logger = logging.getLogger("ncbi_taxonomy.lineage_pruner.LineagePruner")
        #self.logger.setLevel(logging.ERROR)


    def prune_unnecessary(self):
        self.prune_unnecessary_taxa(self.unnecessary_list)



    def prune_unnecessary2(self, use = False):
        #self.logger.error((self.lineage.leaf_taxon.name, self.lineage.taxon_list[-1].taxon.name)) 
        #self.logger.error([t.level for t in self.lineage.taxon_list])
        for level in reversed(self.lineage.default_levels):
            if use:
                tax, unn= self.lineage.get_closest_unnecessary_by_level(level)
                self._update_unnecessary(tax, unn, level)
            self._prune_unnecessary_by_level(level)
        #self._update_hierarchy()
       
        #self.logger.error([t.level for t in self.lineage.taxon_list])
         

    def update_hierarchy(self):
        """
            TODO!!! requires the logging methods!!!

            this method accepts only the final taxon list
            where all we need to check if the consecutive
            taxa has a child-parent relationship. if not
            set the relationshp.

        """
        
        if sorted([tax.level for tax in self.lineage.taxon_list]) != sorted(self.lineage.default_levels):
            raise Exception("Required taxonomic levels are not satisfied yet.")


        for i in range(len(self.lineage.taxon_list)-1):
            child_tax= self.lineage.taxon_list[i]
            parent_tax= self.lineage.taxon_list[i+1]
             

            #try:
            hier= self.lineage.biodb_selector.store.find(Hierarchy, Hierarchy.childID == child_tax.taxon.id ).one()
            
            #except:
            #    continue

            if hier.parent.id != parent_tax.taxon.id:
                new_hier= Hierarchy()
                new_hier.parentID= parent_tax.taxon.id
                new_hier.childID= child_tax.taxon.id

                self.lineage.biodb_selector.store.remove(hier) 
                self.lineage.biodb_selector.store.add(new_hier)

                child_id= child_tax.taxon.id
                old_parent_id= hier.parentID
                new_parent_id= parent_tax.taxon.id
                #self.logger.error("child id: %d, old parent id: %d, new parent id: %d" %(child_id, old_parent_id, new_parent_id))
                #self.logger.error("child name: %s, old parent name: %s, new parent name: %s" %(child_tax.taxon.name, hier.parent.name, parent_tax.taxon.name))
                ### DONT FORGET TO COMMIT

        self.lineage.biodb_selector.store.commit()


    def prune_unnecessary_taxon(self, tax, unn):
        self.lineage.taxon_list.remove(tax)
        self.lineage.unnecessary_list.remove(unn)
            
    
    def prune_unnecessary_taxa(self, unna):
        taxa= [self.lineage.get_taxon(unn) for unn in unna]
        
        #if taxa !=  []:
            #self.logger.info("Leaf: %s" %self.lineage.leaf_taxon.name)
            #self.logger.info(taxa)
            #self.logger.info("#####")
        
        self.lineage.taxon_list= [tax for tax in self.lineage.taxon_list if tax not in taxa]
        self.lineage.unnecessary_list= [unn for unn in self.lineage.unnecessary_list if unn not in unna]
    


    def prune_unnecessary_by_level(self, level):
        """
        prunes the unnecessary taxa between the inquired 
        level rank and its parent.
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

                self._prune_unnecessary_taxa(unn_to_be_pruned)

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
                   

                    #if unn_to_be_pruned != []:
                        #self.logger.error(level)
                        #self.logger.error([t.level for t in self.lineage.taxon_list])
                        #self.logger.error(unn_to_be_pruned)


                    #self.logger.info(unn_to_be_pruned)
                    #self.logger.info("####")               
                            
                #elif level == 6:
                    
                #    for unn in self.lineage.unnecessary_list:
                #        if unn.index > taxon.index:
                #            unn_to_be_pruned.append(unn)
                



                self._prune_unnecessary_taxa(unn_to_be_pruned)
                        

    def replace_required(self, feature):      
        """
            TODO: to be checked
            not a pruner function. replaces reuqired taxon names if their super/sub 
            ranks exist!
        
        """
        #for taxon in mock_taxa_2:
        #lineage= self.getTaxonomy(self.getFeatureByID(4049))
        #lineage= getTaxonomy(feature)
        ranks= [f.level for f in lineage]
        
        found_ranks= set(ranks).intersection(set(range(1,7)))
        different_ranks= set(ranks).difference(set(range(1,7)))

        if found_ranks != set(range(1,7)):
            #print hier
            required_ranks = set(range(1,7)).difference(set(found_ranks))
            rank_names= [extended_level_dict[rank] for rank in ranks]
            for rank in required_ranks:
                rankname = extended_level_dict[rank]
                ### super_rank
                if "super%s"%rankname in rank_names: 
                    ### super finding alert!!!
                    ### here we perform update operations
                    ### the previous parentIDs will be changed
                    prefix = "super"

                elif "sub%s"%rankname in rank_names:
                    prefix = "sub"

                elif "no rank" in rank_names:
                    prefix= "no rank "
                
                for level in different_ranks:
                    new_rank= "%s%s" % (prefix, rankname)
                    if extended_level_dict[level] == new_rank:
                        ### our beloved feature
                        ### change both the name and level of this
                        ### feature. add (prefix + rankname) to the 
                        ### name.
                        required_level = extended_levels.index(rankname) + 1  
                        index_ = ranks.index(level)
                        tax_upd= lineage[index_]
                        tax_upd.level = required_level
                        tax_upd.name = "%s (%s)" % (tax_upd.name, level)
                    
                    elif new_rank == "no rank %s" %rankname:
                        required_level = extended_levels.index(rankname) + 1 
                        index_ = ranks.index("no rank")
                        tax_upd= lineage[index_]
                        tax_upd.level = required_level
                        tax_upd.name = "%s (%s)" % (tax_upd.name, new_rank)
                        ## this won't work if unranked level is 
                        ## not placed at the same level.
                        #s.store.commit()



                     
    def update_unnecessary(self, tax, unn_tax, level):
        tax.level = level
        self.lineage.unnecessary_list.remove(unn_tax)
     

    #def prune_unnecessary(self):
    #    for k, g in groupby(enumerate(ranks), lambda (i, x): x > 6):

trash = """

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


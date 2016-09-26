from itertools import groupby
from operator import itemgetter
from collections import Counter

import numpy as np

from sqling.selector import Selector
from sqling.storm_objects import Hierarchy, BioDB


s= Selector("ncbi")

def getTaxonomy(feature, lineage=None):
    if lineage == None:
        lineage = [feature]

    hier= s.store.find(Hierarchy, BioDB.id == Hierarchy.parentID, Hierarchy.childID == feature.id).one()

    if hier:
        lineage.append(hier.parent)

        if hier.parent.level != 1:
            getTaxonomy(hier.parent, lineage)
    return lineage




def pruneUnranked(feature):
    """
    first thing to do after detecting that 
    the lineage is not normal
    """
    
    lineage= getTaxonomy(feature)
    ranks= [f.level for f in lineage]
    if 11 in ranks:
        for k, g in groupby(enumerate(ranks), lambda (i, x): x):
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
                #self.store.commit()
    
    return getTaxonomy(feature)
   



def pruneConsecutive(feature):
    """
        prune only the ranks > 6.
    """    
    lineage= getTaxonomy(feature)
    ranks= [f.level for f in lineage]

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
    
    return getTaxonomy(feature)


def replaceRequired(feature):      
    #for taxon in mock_taxa_2:
    #lineage= self.getTaxonomy(self.getFeatureByID(4049))
    lineage= getTaxonomy(feature)
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
    return getTaxonomy(feature)


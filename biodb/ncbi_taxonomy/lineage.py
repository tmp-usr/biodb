from taxon import Taxon
from biodb.sqling.selector import Hierarchy, BioDB

import pdb


extended_levels= ["phylum", "class", "order", "family",
                  "genus", "species", "forma", "infraclass",
                  "infraorder", "kingdom", "no rank",
                  "parvorder", "species group", "species subgroup",
                  "subclass", "subfamily", "subgenus", "subkingdom",
                  "suborder", "subphylum", "subspecies", "subtribe",
                  "superclass", "superfamily", "superkingdom",
                  "superorder", "superphylum", "tribe", "varietas"]


class Lineage(object):
    """
        Lineage class containing the hierarchical list of Taxon objects.
    
    """
    
    def __init__(self, feature, biodb_selector):


        self.leaf_taxon= feature
        self.biodb_selector= biodb_selector
        
        lineage= self.get_lineage_from_biodb(feature)

        taxon_list= [Taxon(feature, self.biodb_selector, index) for 
                index, feature in enumerate(lineage)]
        
        self.taxon_list= taxon_list
        self.default_levels = range(1,7)

        self.existing_taxa=[] 
        self.unnecessary_list= [] 
    
        self.load_lineage()
    
    
    def get_lineage_from_biodb(self, feature=None, lineage=None):
        
        if lineage == None:
            lineage = [feature]

        hier= self.biodb_selector.store.find(Hierarchy, BioDB.id == Hierarchy.parentID, Hierarchy.childID == feature.id).one()

        if hier:
            lineage.append(hier.parent)

            if hier.parent.level != 1:
                self.get_lineage_from_biodb(hier.parent, lineage)
        return lineage



    def get_taxon(self, taxon):
        """
        retrieves the queried taxon from the taxon list of the lineage. 
        useful when we want to inquire the index of an unnecessary taxon 
        in the lineage.
        """
        
        try:
            return [tax for tax in self.taxon_list if tax.index == taxon.index][0]
        except:
            pdb.set_trace()



    def get_closest_taxa_by_level(self, level, taxon_list):
        """
        retrieves multiple taxa that are close to an inquired level.
        useful when we wanna prune the lineage or insert unranked taxa 
        at/to certain levels.
        """
        closest_distance= min([abs(taxon.level-level) for taxon in taxon_list])
        taxa= [taxon for taxon in taxon_list if abs(taxon.level - level) == closest_distance]
        
        while len(taxa) == 1:
            closest_distance+=1
            extended_taxon= [taxon for taxon in taxon_list if 
                    abs(taxon.level - level) == closest_distance  and 
                    abs(taxa[0].level - taxon.level) != 1 ]

            taxa += extended_taxon


        return taxa

    def get_closest_unnecessary_by_level(self, level):
        """
        unnecessary taxa are those that are defined as unranked 
        or those ranked by super or sub prefixes with the level rank. 
        """
        taxa= list(self.get_closest_taxa_by_level(level, self.taxon_list))
        min_index_diff=10
        closest_unnecessary= None
        for unn in self.unnecessary_list:
            for taxon in taxa:
                min_index_diff_upd= abs(taxon.index - unn.index)
                if min_index_diff_upd < min_index_diff:
                    min_index_diff= min_index_diff_upd 
                    closest_unnecessary = unn
        result= self.get_taxon(closest_unnecessary)
        #self.unnecessary_taxa.remove(closest_unnecessary)
        return result, closest_unnecessary
    
        #closest_taxa= [i for i in l.get_closest_taxa(level)]
        #closest= min([abs(taxon.level-closest_taxa[-1].level) for taxon in self.unnecessary_taxa])
        
        #result= []
        #for taxon in closest_taxa:
        #    result+= [taxon for taxon in self.unnecessary_taxa if 
        #           taxon.level > level]
        #return result
    
    def get_taxa_by_level(self, level):
        """
        retrieves a list of taxa* at the inquired level. 
        *there can be multiple taxa from the same level only in 
        the case of unranked levels.
        """
        
        return [taxon for taxon in self.taxon_list if taxon.level == level]

    def level_exists(self, level):
        return level in [tax.level for tax in self.taxon_list]
    
    def load_lineage(self):
        """
        loads the initial lineage hierarchy yielding existing levels
extended_levels= ["phylum", "class", "order", "family",
                  "genus", "species", "forma", "infraclass",
                  "infraorder", "kingdom", "no rank",
                  "parvorder", "species group", "species subgroup",
                  "subclass", "subfamily", "subgenus", "subkingdom",
                  "suborder", "subphylum", "subspecies", "subtribe",
                  "superclass", "superfamily", "superkingdom",
                  "superorder", "superphylum", "tribe", "varietas"]        and unnecessary levels.
        """
        
        self.found_levels= set(self.default_levels).intersection(set(
                self.get_levels())) 
        
        self.different_levels= set(self.get_levels()).difference(set(
                self.default_levels))
        
        self.required_levels= set(self.default_levels).difference(set(
                self.get_levels()))

        
        levels= self.get_levels()
        
        if levels != self.default_levels:
            self.missing_levels= list(set(self.default_levels).difference(set(levels)))
                       
            for level in set(self.default_levels).intersection(set(levels)):
                self.existing_taxa+= self.get_taxa_by_level(level) 
            

            for level in set(levels).difference(set(self.default_levels)):
                self.unnecessary_list+= self.get_taxa_by_level(level)
    
        
        




    
    def get_levels(self):
        return [taxon.level for taxon in self.taxon_list]
    
   

    


    @property
    def lineage_type(self):
        """extended_levels= ["phylum", "class", "order", "family",
                  "genus", "species", "forma", "infraclass",
                  "infraorder", "kingdom", "no rank",
                  "parvorder", "species group", "species subgroup",
                  "subclass", "subfamily", "subgenus", "subkingdom",
                  "suborder", "subphylum", "subspecies", "subtribe",
                  "superclass", "superfamily", "superkingdom",
                  "superorder", "superphylum", "tribe", "varietas"]
        checks if the existing level ranks are sufficient to form a
        hierarchy from species to phylum.
        
        returns lineage_type:
        1: default lineage exists without unnecessary
        2: default lineage exists with additional taxa (sub/super) in between 
        3: default lineage does not exist but there are additional taxa found in between
        default ones.
        4: de fault lineage does not exist and there is no additional taxa found in between the lacking taxon hierarchy
        """

        found_levels= set(self.default_levels).intersection(set(
                self.get_levels())) 
        
        different_levels= set(self.get_levels()).difference(set(
                self.default_levels))
        
        required_levels= set(self.default_levels).difference(set(
                self.get_levels()))
        

        if found_levels == set(self.default_levels) and len(self.taxon_list) == len(self.default_levels):
            return 1

        elif found_levels == set(self.default_levels) and len(self.taxon_list) > len(self.default_levels):
            return 2

        
        elif required_levels != set():
            ### first try to solve the problem with the existing ranks
            ### e.g include sub/super (rank) in the lineage
            #Required= {}
           
            if len(self.taxon_list) < len(self.default_levels):
                return 4

            required_level=  list(required_levels)[0]
            taxa= self.get_closest_taxa_by_level(required_level, self.taxon_list)
            try:
                n_required_unnecessary= self.taxon_list.index(taxa[1]) - self.taxon_list.index(taxa[0]) - 1
           
            except:
                if required_level == 1:
                    n_required_unnecessary= self.taxon_list.index(taxa[0]) - 1
            
                elif required_level == 6:
                    n_required_unnecessary = self.taxon_list.index(self.taxon_list[-1]) - self.taxon_list.index(taxa[0]) - 1

                #print required_level, n_required_unnecessary
                #print "###########"
                #print taxa, self.taxon_list
                #continue
            
            

            #try:
            if n_required_unnecessary > 0:                
                
                return 3
            #except:
            #    pdb.set_trace()
                #return (3, required_level, n_required_unnecessary)
           

            else:
                return 4
                #return (4, required_level, 0)

                #for taxon in taxa:
                #    print self.leaf_taxon.name
                #print "found level: %s , required_level: %s, n_required_unnecessary: %s" %(taxa[0].level, required_level, n_required_unnecessary)    
                    #    print "######"
                    
            #for level in required_levels:
            #    result, unn= self.get_closer_unnecessary_by_level()
                



trash = """
            rank_names= [extended_levels[level-1] for level in self.get_levels()]
            required_level_names= extended_levels[level-1] for level in required_levels]
            
            for required_level_name in required_level_names:
                
                prefix =""

                if "super%s"%required_level_name in rank_names: 
                    ### super finding alert!!!
                    ### here we perform update operations
                    ### the previous parentIDs will be changed
                    prefix = "super"

                elif "sub%s"%required_level_name in rank_names:
                    prefix = "sub"

                
                if prefix != "":

                    for level in different_levels:
                    

            ### if sub/super (rank) is not found in the lineage, search
            ### for "no rank"s in the index range of the lacking ranks.
"""            
             

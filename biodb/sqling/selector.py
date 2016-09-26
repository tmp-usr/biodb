from collections import OrderedDict

from storm.locals import create_database, Store, Select
from paketbuiol.io_helper import BatchReader
#from storm_objects import BioDB, Hierarchy


from biodb_base import BioDBBase
from biodb_base import BioDB, Hierarchy, Lineage

import pdb


def find_all_paths(graph, start, end, path=[]):
    
    path = path + [start]
    if start == end:
        return [path]
    
    if not graph.has_key(start):
        return []
    paths = []
    
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths




class Selector(BioDBBase):
    
    def __init__(self, db_name):    
        self.db_name = db_name
        BioDBBase.__init__(self, db_name)
        self.init_table()

        self.extended_levels= ["phylum","class","order","family","genus","species","forma","infraclass","infraorder","kingdom","no rank","parvorder","species group","species subgroup","subclass","subfamily","subgenus","subkingdom","suborder","subphylum","subspecies","subtribe","superclass","superfamily","superkingdom","superorder","superphylum","tribe","varietas"]
    

    def getLevelStats(self):
        nLevels= self.getLevelCount()
        total= 0
        for level in range(1, nLevels+1):
            features= self.getFeaturesByLevel(level)
            total+= len(features)
            print level, len(features)
        print "%s features in total" %total

    def getNameByID(self, id):
        return self.store.get(BioDB,id).name

    def getFeatureByID(self,id):
        return self.store.get(BioDB,id)

    def getNameByAccession(self, accession):
        return self.getNameByID(self.getIDByAccession(accession))

    def getFeatureByAccession(self, accession):
        return self.store.find(BioDB,BioDB.accession == accession).one()

    def getIDByName(self, name,level):
        return self.store.find(BioDB, (BioDB.name.lower() == name.lower()) & (BioDB.level==level)).one().id

    def getIDByAccession(self, accession):
        return self.store.find(BioDB, (BioDB.accession==accession)).one().id

    def getChildrenByParentID(self, parentID,level):
        """
            some pathways are repeated with the same name at different levels. although we wouldn't have required the level argument for this funcion, in order to double check that the given parentID is the one at the level we are looking for, level should be valid parameter.  
        """
        return [item for item in self.store.find(BioDB, BioDB.id == Hierarchy.childID, BioDB.level == level+1, Hierarchy.parentID == parentID)]

    def getParentsByChildID(self, childID):
        results= self.store.find(BioDB, BioDB.id == Hierarchy.parentID, Hierarchy.childID == childID)
        return list(results) 

    def getFeatureByName(self, name,level):
        return self.store.find(BioDB, (BioDB.name==name) & (BioDB.level==level)).one()

    def getChildNamesByParentID(self, parentID):
        return [(item.name,item.accession) for item in self.store.find(BioDB, BioDB.id == Hierarchy.childID, Hierarchy.parentID == parentID)]

    def isUniqueFeature(self, feature, nPathways):
        parents= self.getParentsByChildID(feature.id)
        return len(parents) <= nPathways

    def getUniqueEnzymesByPathwayLimit(self, pathway, nPathways):
        """
            returns an enzyme generator for the unique enzymes of the pathway defined by the maximum number of pathways that the enzyme can be involved (nPathways)!
        """
        assert pathway.level < self.getLevelCount(), 'Selected feature is not a pathway!'
        children= self.getChildrenByParentID(pathway.id, pathway.level)
        for child in children:
            if len(self.getParentsByChildID(child.id)) <= nPathways:
                yield child


    def getChildrenByLevel(self, level):
        Children={}
        resultList= self.store.find(Hierarchy, BioDB.id == Hierarchy.childID, BioDB.level == level+1)
        
        for item in resultList:
            if item.parent.name not in Children:
                Children[item.parent.name]=[]
            Children[item.parent.name].append(item.child)
        return Children
      
    
    def getUniqueChildrenByFeature(self, feature):
        children=[]
        resultSet= self.store.find(BioDB, BioDB.id == Hierarchy.childID, Hierarchy.parentID == feature.id )
        for item in resultSet:
            parentSet= self.store.find(BioDB, BioDB.id == Hierarchy.parentID, Hierarchy.childID == item.id)
            if len(list(parentSet)) == 1:
                children.append(item)
        return children

    #deprecated
    #def getChildNamesByParentName(self,store, parentID,level):
    #    return [(f.name,f.accession) for f in store.find(BioDB, BioDB.parentID == parentID,level))]

    def getFeaturesByLevel(self,level, chunk_size = 0):
        level_feature_generator= self.store.find(BioDB,BioDB.level == level)
        
        if chunk_size:
            return BatchReader(chunk_size, level_feature_generator)
        
        else:
            return list(level_feature_generator)

    def getLevelCount(self):
        return max([item[0] for item in self.store.execute(Select(BioDB.level, distinct=True))])


    def buildLineageHierarchy(self,child, hier=None):
        '''
            traverse the lineage tree starting from child
        '''
       
        if hier is None:
            hier= []
        
        if child.level != 1:
            hier.append(child)
                #print [h.name for h in hier]
            child= self.store.find(BioDB, BioDB.id == Hierarchy.parentID, Hierarchy.childID == child.id)[0]
            self.buildLineageHierarchy(child, hier)
        else:
            hier.append(child)
        return hier 
    
        return self.buildLineageHierarchy(child)
    
    def buildLineageGraph(self, feature, Parent=None, Level=None):
        
        if Parent is None:
            Parent={}
        
        if Level is None:
            Level={}
            Level[feature.level+1]=[feature.name] 
        

        if feature.level != 1:

            resultList= self.store.find(Hierarchy, BioDB.id == Hierarchy.parentID, Hierarchy.childID == feature.id)
            
            for f in resultList:
                if feature.name not in Parent:
                    Parent[feature.name]=[]    
                Parent[feature.name].append(f.parent.name)
                
                
                if feature.level not in Level:
                    Level[feature.level]=[]    
                Level[feature.level]+=[f.parent.name]
                
                #if f.name not in Parent:
                #    Parent[f.name]=[]
                #Parent[f.name].append(feature.name)
                self.buildLineageGraph(f.parent,Parent,Level)
                
        return Parent,Level


    def getLeafNodesByParent(self, parent, endLevel, path=None):
        if path == None:
            path=[]
    
        if parent.level == endLevel+1:
            return path

        if parent.level == endLevel: 
            path.append(parent)
        
        for feature in self.getChildrenByParentID(parent.id, parent.level):
            self.getLeafNodesByParent(feature, endLevel, path)
        
        return path


    def mapLeafNodesByLevel(self, level, endLevel):
        leafNodeLevel=self.getLevelCount()
        leafNodeMapping=dict.fromkeys(self.getFeaturesByLevel(level),[])
        
        for k in leafNodeMapping.keys():
            leafNodeMapping[k]=self.getLeafNodesByParent(k, endLevel)
        
        return leafNodeMapping


    def buildTaxonomyGraph(self, feature, Parent=None, Level=None):
        """
            This function will be changed with a tree traversal function instead.
            Taxonomic groups are organized in the NCBI taxonomy database as trees 
            and not as DAG structure as opposed to the functional databases.
            This change will eliminate the two-step traversal with the taxonomy
            formation and lineage retrieval to one step tree traversal (check the 
            time differences in the two approaches.) 

        """


        if Parent is None:
            Parent=OrderedDict()
        
        if Level is None:
            Level=OrderedDict()
            Level[feature.level]=[feature] 
        

        if feature.level != 1:

            resultList= self.store.find(Hierarchy, BioDB.id == Hierarchy.parentID, Hierarchy.childID == feature.id)
            
            for f in resultList:
                if feature not in Parent:
                    Parent[feature]=[]    
                Parent[feature].append(f.parent)
                
                
                if feature.level not in Level:
                    Level[feature.level]=[]    

                else:
                    self.buildTaxonomyGraph(f.parent,Parent,Level)
                
                Level[feature.level]+=[f.parent]
                self.buildTaxonomyGraph(f.parent,Parent,Level)
        

        return Parent,Level


    def getTaxonomicLineage(self, taxon):
        """
            The function 'getLineages' was written according to the default
            fantom database input file processing where higher hierarchy level
            categories always have lower ids than their children. NCBI taxonomy
            database is curated a bit more chaotic in contrast to the default
            accepted format in fantom. Retrieving the lineage tree in this
            version will rely on the ranks (levels) of individual taxa as opposed
            to the startNo given in the second line of the previous version.
            >> startNo = max(sorted(Level(keys()))) OUT
            >> startNo = [f.level for f in [self.getFeatureByID(id) for id in             
            Level.keys()]
            
        """
        feature = taxon
        Parent,Level=self.buildTaxonomyGraph(feature)
        
        startNo= max(sorted(Level.keys()))

        endNo=min(sorted(Level.keys()))

        
        start=Level[startNo][0]
        ends=list(set(Level[endNo]))
        
        Lineages={}
        Lineages[start]=[]
        for end in ends:
            for path in find_all_paths(Parent, start, end):
                Lineages[start].append('; '.join(path[1:]))
        Lineages[start]=list(set(Lineages[start]))
         
        return Lineages

    def getLineage(self, feature, lineage=None):
        
        if lineage == None:
            lineage = [feature]

        hier= self.store.find(Hierarchy, BioDB.id == Hierarchy.parentID, Hierarchy.childID == feature.id).one()
        
        if hier:
            lineage.append(hier.parent)
        
            if hier.parent.level != 1:
                self.getLineage(hier.parent, lineage)
         
        return lineage


    def pruneUnranked(lineage):
        """
        first thing to do after detecting that 
        the lineage is not normal
        """
        
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

                    s.store.commit()


    def pruneConsecutive(self, lineage):
        """
            update this function by only processing ranks > 6
        """
             
        ranks= [f.level for f in lineage]
        for k, g in groupby(enumerate(ranks), lambda (i, x): i+x):
            g=[i for i in g]
            list_ranks= map(itemgetter(1), g)
            list_indexes= map(itemgetter(0), g)
            if set(list_ranks).difference(set(range(1,7))) != set():
                child_taxon= lineage[list_indexes[0]-1]
                parent_taxon= lineage[list_indexes[-1]+1]
                hier= self.store.find(Hierarchy, Hierarchy.childID == \
                                   child_taxon.id ).one()
                hier.parentID= parent_taxon.id
                self.store.commit()



    def pruneAndReplaceRequired(self, lineage):      
        #for taxon in mock_taxa_2:
        #lineage= self.getTaxonomy(self.getFeatureByID(4049))
        ranks= [f.level for f in lineage]
        found_ranks= set(ranks).intersection(set(range(1,7)))
        different_ranks= set(ranks).difference(set(range(1,7)))

        if len(lineage) > 7 and found_ranks != set(range(1,7)):
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
                        s.store.commit()
            
            s.pruneTaxonomy()





    def pruneNCBITaxonomy(self, lineage):
        ranks= [f.level for f in lineage]

        if ranks != reversed(range(1,7)):
            if len(ranks) > 6:
                found_ranks= set(ranks).intersection(set(range(1,7)))
                if found_ranks == set(range(1,7)):
                    # lineage includes all the required taxonomic ranks for fantom
                    ### easier to prune
                    self.pruneConsecutive(lineage)
                
                else:
                    required_ranks = set(range(1,7)).difference(set(found_ranks))
                    ### check if any closer rank exists among the lineage to the
                    ### required ranks

                    rank_names= [self.extended_level_dict[rank] for rank in ranks]
                    for rank in required_ranks:
                        rankname = self.extended_level_dict[rank]
                        ### super_rank
                        if "super%s"%rankname in rank_names: 
                            ### super finding alert!!!
                            ### here we perform update operations
                            ### the previous parentIDs will be changed
                            prefix = "super"
                        
                        elif "sub%s"%rankname in rank_names:
                            prefix = "sub"

                        for feature in lineage:
                            if self.extended_level_dict[feature.level] == \
                                "%s%s" % (prefix, rankname):
                                    ### our beloved feature
                                    ### change both the name and level of this
                                    ### feature. add (prefix + rankname) to the 
                                    ### name.
                                    pass 
                         
                        
            


    def getLineages(self, feature):
        Parent,Level=self.buildLineageGraph(feature)
        startNo= max(sorted(Level.keys()))

        endNo=min(sorted(Level.keys()))

        
        start=Level[startNo][0]
        ends=list(set(Level[endNo]))
        
        Lineages={}
        Lineages[start]=[]
        for end in ends:
            for path in find_all_paths(Parent, start, end):
                Lineages[start].append('; '.join(path[1:]))
        Lineages[start]=list(set(Lineages[start]))
        
        #pdb.set_trace()

        return Lineages


    def buildLineageGraph2(self, feature, Parent=None, Level=None):
        
        if Parent is None:
            Parent=OrderedDict()
        
        if Level is None:
            Level=OrderedDict()
            Level[feature.level]=[feature] 
        

        if feature.level != 1:

            resultList= self.store.find(Hierarchy, BioDB.id == Hierarchy.parentID, Hierarchy.childID == feature.id)
            
            for f in resultList:
                if feature not in Parent:
                    Parent[feature]=[]    
                Parent[feature].append(f.parent)
                
                
                if feature.level not in Level:
                    Level[feature.level]=[]    
                Level[feature.level]+=[f.parent]

                self.buildLineageGraph2(f.parent,Parent,Level)
                
        return Parent,Level


    def getLineages2(self, feature):
        Parent,Level=self.buildLineageGraph2(feature)
        startNo= max(sorted(Level.keys()))

        endNo=min(sorted(Level.keys()))
        
        start= Level[startNo][0]
        ends= list(set(Level[endNo]))
        
        Lineages={}
        Lineages[start]=[]
        for end in ends:
            for path in find_all_paths(Parent,start,end):
                Lineages[start].append(tuple(path[1:]))
        Lineages[start]=list(set(Lineages[start]))
        #pdb.set_trace()
        return Lineages




        

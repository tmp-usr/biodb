from storm.locals import *

class BioDB(object):
    __storm_table__ = 'biodb'
    id = Int(primary=True)
    name = Unicode()
    accession=Unicode()
    level = Int()

    def __init__(self, id, accession, name, level):
        self.id = id
        self.accession = accession
        self.name= name
        self.level= level


class Lineage(object):
    __storm_table__ = "lineage"
    id= Int(primary=True)
    childID= Int()
    lineage=Unicode()

class Hierarchy(object):
    __storm_table__ = 'hier'
    __storm_primary__='childID','parentID'
    childID=Int()
    parentID=Int()
    child=Reference(childID, BioDB.id)
    parent=Reference(parentID, BioDB.id)

class NCBIDivision(object):
    __storm_table__="biodb_ncbi_division"
    id= Int(primary=True)
    name= Unicode()

class NCBITaxonomyDivision(object):
    __storm_table__= 'biodb_ncbi_taxonomy_division'
    taxonID= Int(primary= True)
    divisionID= Int()
    taxon= Reference(taxonID, BioDB.id)
    division= Reference(divisionID, NCBIDivision.id)

class NCBIHierUpdate(object):
    __storm_table__= "biodb_ncbi_hier_update"
    taxonID= Int(primary= True)
    oldParentID= Int()
    newParentID= Int()
    taxon= Reference(taxonID, BioDB.id)
    old_parent= Reference(oldParentID, BioDB.id)
    new_parent= Reference(newParentID, BioDB.id)


class NCBITaxonUpdate(object):
    __storm_table__ = "biodb_ncbi_biodb_update"
    taxonID= Int(primary= True)
    oldName= Unicode()
    newName= Unicode()
    oldLevel= Int()
    newLevel= Int()



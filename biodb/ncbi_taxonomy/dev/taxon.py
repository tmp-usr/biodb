class Taxon(object):
    def __init__(self, feature, biodb_selector, index, rank=""):
        self.taxon= feature
        self.level= self.taxon.level
        self.rank= rank
        self.index= index
    
    def __str__(self):
        return "name:%s, index:%s, level:%s" %(self.taxon.name, self.index, self.level)
    
    def __repr__(self):
        return "name:%s, index:%s, level:%s" %(self.taxon.name, self.index, self.level)



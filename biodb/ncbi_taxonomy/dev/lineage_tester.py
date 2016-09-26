from __future__ import print_function

from pprint import pprint as pp

from biodb.sqling.selector import Selector
from lineage import Lineage
import unittest

class LineageTests(unittest.TestCase):

    def setUp(self):
        
        self.biodb_selector= s= Selector("ncbi")
        #self.feature= self.biodb_selector.getFeatureByID(781)
        self.feature= self.biodb_selector.getFeatureByID(89)
        self.lineage = Lineage(self.feature, self.biodb_selector)

    def test_lineage_loading(self):
        self.failIf(len(self.lineage.existing_list) > len(self.lineage.default_levels))
     
    def test_levels(self):
        self.failIf(self.lineage.get_levels() != [t.level for t in self.lineage.taxon_list])

    def test_taxon_retrieval(self):
        self.failIf(self.lineage.get_taxa_by_level(2)[0].taxon.level != 2)
   
    def test_level_exists(self):
        self.failIf(self.lineage.level_exists(3) != True)

    def test_closest_taxon_retrieval(self):
        self.failIf(self.lineage._get_closest_taxa_by_level(4, self.lineage.taxon_list)[0].taxon.id < 0)

    def test_closest_unn_retrieval(self):
        unn= self.lineage.get_closest_unnecessary_taxon_by_level(4)
        self.failIf(unn is None)
    


def main():
    unittest.main()

if __name__ == '__main__':
    main()

import unittest
from collections import Counter

from biodb.sqling.updater import Updater
from biodb.sqling.selector import Selector
from biodb import sql_db_path


class BioDBTests(unittest.TestCase):
   
    #def test_foo(self):
    #    self.failUnless(False)
    def setUp(self):
        self.updater = Updater("kegg_orthology_metabolism", '../'+sql_db_path)
        self.updater.store_database()
        self.selector= Selector("kegg_orthology_metabolism", '../'+sql_db_path)

    def test_biodb(self):
        """
        checks if the biodb table exists and returns how many features are inserted.
        """
        print "testing biodb table"
        table_list= [table[0] for table in self.updater.store.execute('select tbl_name from SQLITE_MASTER')]
        self.failIf(self.updater.biodb_table not in table_list)
        #assert self.biodb_table in table_list, "Table does not exist!"


    def test_hierarchies(self):
        """
        checks if hierarchies table exists and returns how many hierarchies are built.
        """
        print "testing hierarchy table"
        table_list= [table[0] for table in self.updater.store.execute('select tbl_name from SQLITE_MASTER')]
        self.failIf(self.updater.hier_table not in table_list)
        

    def test_names_acessions(self):
        """
        checks the uniqueness of names
        """
        print "testing uniqueness of names in each level."
        levelCount = self.selector.getLevelCount()
        for i in range(1, (levelCount+1)): 
            children= self.selector.getFeaturesByLevel(i)
            names= [feature.name for feature in children]
            name_counter= Counter(names)
            for k,v in name_counter.iteritems():
                if v != 1:
                    print k, v
            self.assertEqual(len(names), len(set(names)))

    def test_levels(self):
        """
        1. checks if all leaf nodes have the same level of hierarchies
        2. checks if each feature and its parent have max 1 level in between
        """
        print "testing number of hierarchy levels for each leaf node"
        print "testing if a parent is exactly one level higher than the child in the database hierarchy."
        leaf_features= self.selector.getFeaturesByLevel(self.selector.getLevelCount())
        for feature in leaf_features:    
            lineage= self.selector.getLineages2(feature)
            for v in lineage.values():
                for lin in v:
                    if len(lin) >= 1:
                        nLevels= self.selector.getLevelCount()
                        self.failIf( len(lin) > (nLevels - 1) )
                        diff= feature.level - lin[0].level
                        self.failIf(diff != 1)
                        
                        levels= [i.level for i in lin]
                        self.failIf(levels != range(1,nLevels)[::-1])


    def test_print_stats(self):
        print "Database stats:"
        self.selector.getLevelStats()
    
    def compare_new_with_current_version(self):
        ### currently this task is done by checking database log files from the database source provider
        print "You already have this database in fantom db. If you still want to update the existing database, insert a different database name (e.g kegg_orthology_2) and try again!"


    def no_test_insertions(self):
        ### eliminate the hierarchy groups which don't have appropriate number of levels
        ### 1. check if there is one level between the child and parent hierarchy objects
        for i in range(2, self.selector.getLevelCount()):
            features= self.getFeaturesByLevel(i)
            for feature in features:
                resultList= self.store.find(Hierarchy, BioDB.id == Hierarchy.parentID, Hierarchy.childID == feature.id)
                for result in resultList:
                    #print result.parent.level - feature.level
                   if (feature.level - result.parent.level) > 1:
                        print feature.name, result.parent.name
                        print feature.level, result.parent.level
                        print 



def main():
    unittest.main()

if __name__ == '__main__':
    main()


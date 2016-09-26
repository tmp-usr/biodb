from __future__ import print_function

from pprint import pprint as pp

from biodb.sqling.selector import Selector
from lineage import Lineage
from lineage_pruner import LineagePruner
import logging


import unittest




class LineageTests(object):

    def __init__(self):    
        self.biodb_selector= s= Selector("ncbi")
        all_species= self.biodb_selector.getFeaturesByLevel(6)
        mock_species= all_species[:2500]
        
        # lineage type 2
        #self.feature= self.biodb_selector.getFeatureByID(35)
        ## lineage type 3
        
        for taxon in mock_species:
            self.feature= taxon
            self.lineage = Lineage(self.feature, self.biodb_selector)
            self.lineage_pruner= LineagePruner(lineage=self.lineage)
            self.lineage_pruner.use_unnecessary_and_prune()
    

    def set_logger(self):
        # create logger with "spam application"
        self.logger= logging.getLogger("ncbi_taxonomy")
        self.logger.setLevel(logging.DEBUG)

        # create a file handler 
        fh= logging.FileHandler("ncbi_taxonomy.log")
        fh.setLevel(logging.DEBUG)

        # create a console handler
        ch= logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        # set formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s- %(levelname)s - %(message)s", 
                datefmt='%m/%d/%Y %I:%M:%S %p')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)


    def test_prune_unnecessary(self):
        """
            worked with 
        """
        pp(self.lineage.taxon_list)
        #self.lineage_pruner.prune_unnecessary()
        #print()
        #if len(self.lineage.taxon_list) != 6:
        #    pdb.set_trace()
            #raise Exception("Something wrong")


LineageTests()


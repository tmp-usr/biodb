from itertools import groupby
from operator import itemgetter
import numpy as np
from collections import OrderedDict
import math


import pdb


a= range(1,7)
b= [25,11,2,11,11,4,11,11,11,11]


missing= set(a).difference(set(b))
existing= set(a).intersection(set(b))

b_indexed= OrderedDict(enumerate(b))

minim= lambda myList, myNumber: min(myList, key=lambda x:abs(x-myNumber))

for missing_item in missing:
    item= minim(b_indexed.values(), missing_item)
    if item < missing_item:
        for k, g in groupby(enumerate(b), lambda (i, x): i < x):
            print "smaller", item, missing_item
            print map(itemgetter(1), g)

    elif item > missing_item:

        for k, g in groupby(enumerate(b), lambda (i, x): i > x):
            print "greater", item, missing_item
            print map(itemgetter(1), g)


    #elif item > missing_item:
    #    print  "greater", item, missing_item

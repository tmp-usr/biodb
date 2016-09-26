from itertools import groupby
from operator import itemgetter
import numpy as np
from collections import OrderedDict
import math


import pdb


a= range(1,7)
b= [25,11,2,11,11,4,11,11,11,11]


b_indices = OrderedDict(enumerate(b))

existing_indices= OrderedDict()
remaining_indices= OrderedDict()

for k,v in b_indices.iteritems():
    if v in a:
        existing_indices[v] = k

    else:
        if v not in remaining_indices:
            remaining_indices[v] = []
        remaining_indices[v].append(k)


missing_values= set(a).difference(set(b))

print "existing: ", existing_indices
print "unnecessary: ",remaining_indices
print "missing: ", missing_values

minim= lambda myList, myNumber: min(myList, key=lambda x:abs(x-myNumber))

missing_found= OrderedDict()
found_missing= {}
for missing in missing_values:
    for existing, existing_index in existing_indices.iteritems():
        if missing < existing:
            for remaining, indices in remaining_indices.iteritems():
                minim(indices, existing_index)
                for remaining_index in indices:
                    if remaining_index < existing_index:
                        if (remaining, remaining_index) not in found_missing:
                            
                             
                            found_missing[(remaining, remaining_index)]= 1
                            missing_found[missing] = (remaining, remaining_index)
                            print "missing < existing"
                            print "missing: %s, existing: %s, remaining: %s, remaining_index: %s" %(missing, existing, remaining, remaining_index)

                            break
                        #del remaining_indices[remaining]

        elif missing > existing:
            for remaining, indices in remaining_indices.iteritems():
                for remaining_index in indices:
                    if remaining_index > existing_index:
                        if (remaining, remaining_index) not in found_missing:
                            found_missing[(remaining, remaining_index)]= 1
                            missing_found[missing]= (remaining, remaining_index)
                            print "missing > existing"
                            print "missing: %s, existing: %s, remaining: %s, remaining_index: %s" %(missing, existing, remaining, remaining_index)
                            break
                        #del remaining_indices[remaining]

#for k,v in missing_found.iteritems():
#    print k,v

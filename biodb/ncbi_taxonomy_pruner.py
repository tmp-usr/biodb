from itertools import groupby
from operator import itemgetter
import numpy as np

import pdb


a= range(1,7)
b= [25,11,2,11,11,4,11,11,11,11]

algorithm= """
1. enumerate rank indices
2. define missing ranks
3. extract the indices of unneccessary ranks 
4. define the ranges of existing ranks
5. check if 

"""
algorithm2= """
#1. take the indices of anything not in a 
1. take the indices of the ones in a
2. list the ranges of existing indices 
3. list the ranges of missing
"""






existing= []
unnec= []
for k, g in groupby(enumerate(b), lambda (i, x): x ):
    g=[i for i in g]
    list_ranks= map(itemgetter(1), g)
    list_indices= map(itemgetter(0), g)
   
#    print list_ranks, list_indices

    if list_ranks in np.array(a):
        existing+= zip(list_ranks, list_indices)
    else:
        unnec+= zip(list_ranks, list_indices)

print existing

missing = set(range(1,7)).difference(set(map(itemgetter(0), existing)))

print missing

existing_ranks= map(itemgetter(0),existing)
existing_ends= a[0] in b 

#### ranges of existing ranks
ranges = []
for k, g in groupby(enumerate(existing_ranks),  lambda (i,x):i-x):
    group = map(itemgetter(1), g)
    ranges.append((group[0], group[-1]))

#if ranges[0][0] != 1:
#    ranges.insert(0, (0,1))

#if ranges[-1][-1] != 6:
#    ranges.insert(-1, (6,6))

#### list of required ranges
required_ranges=[]
if len(ranges) > 1:
    for i in range(len(ranges)-1):
        required_ranges.append(sorted((ranges[i+1][0], ranges[i][-1])))

#print required_ranges

for r in required_ranges:
    required_count= r[1] - r[0] -1
    index1= dict(existing)[r[0]]
    index2= dict(existing)[r[1]]
    print index1, index2                    
    for item in map(itemgetter(1),unnec):
        if item in range(index1+1, index2):
            if required_count:
                print item
                required_count-=1




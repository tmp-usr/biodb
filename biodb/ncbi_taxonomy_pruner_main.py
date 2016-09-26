from ncbi_taxonomy_pruner_functions import *

lineage= getTaxonomy(s.getFeatureByID(4718))


a= range(1,7)
b= list(reversed([t.level for t in lineage]))


existing= []
unnec= []
for k, g in groupby(enumerate(b), lambda (i, x): x):
    g=[i for i in g]
    list_ranks= map(itemgetter(1), g)
    list_indices= map(itemgetter(0), g)
    
    if list_ranks in np.array(a):
        existing+= zip(list_ranks, list_indices)
    else:
        unnec+= zip(list_ranks, list_indices)


missing = set(range(1,7)).difference(set(map(itemgetter(0), existing)))

existing_ranks= map(itemgetter(0),existing)


#### ranges of existing ranks
ranges = []
for k, g in groupby(enumerate(existing_ranks),  lambda (i,x):i-x):
    group = map(itemgetter(1), g)
    ranges.append((group[0], group[-1]))

#### list of required ranges

required_ranges=[]
if len(ranges) > 1:
    for i in range(len(ranges)-1):
        required_ranges.append(sorted((ranges[i+1][0], ranges[i][-1])))
#### ranges are now OK! check the ends of the list e.g 1 and 6

print b
print required_ranges


for r in required_ranges:
    required_count= r[1] - r[0] -1
    
    index1= dict(existing)[r[0]]
    index2= dict(existing)[r[1]]
    print index1, index2                    
    for item in map(itemgetter(1),unnec):
        if item in range(index1+1, index2):
            if required_count:
                required_count-=1
                print item



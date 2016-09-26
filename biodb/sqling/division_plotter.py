from ncbi_taxonomy_selector import n_selector
from paketbuiol.io_helper import BatchReader


trash="""

division_lineages= {}
with open("division_lineage_type.txt") as div_lineages:
    br= BatchReader(1000, div_lineages)
    i= 0
    for chunk in br:
        for line in chunk:
            cols= line.rstrip("\n").split("\t")
            
            div_id= cols[0]
            lin_type= cols[1]
            div_name = n_selector.getDivisionNameByID(int(div_id))
               


            if div_name not in division_lineages:
                division_lineages[div_name] = {}

            if lin_type not in division_lineages[div_name]:
                division_lineages[div_name][lin_type] = 0

            division_lineages[div_name][lin_type] += 1
"""


import pickle
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("ggplot")
import collections

#pickle.dump(division_lineages, open("division_lineages.dmp", "w"))

division_lineages= pickle.load(open("division_lineages.dmp"))

for div_name, lineage_type_counts in division_lineages.iteritems():    
   
    sorted_lineage_type_counts = collections.OrderedDict(sorted(lineage_type_counts.items()))

    fig= plt.figure(figsize= (5,3))
    ax= fig.add_subplot(111)
    
    width = 0.5
    ind= np.arange(len(sorted_lineage_type_counts))

    ax.bar(ind+ width/2, sorted_lineage_type_counts.values(), width, color= "blue", alpha= 0.6)
    ax.set_xlabel("Lineage types")
    ax.set_title(div_name)
    ax.set_xticks(ind+width)
    ax.set_xticklabels(map(str, sorted_lineage_type_counts.keys()))

    plt.savefig("%s.png" %div_name)


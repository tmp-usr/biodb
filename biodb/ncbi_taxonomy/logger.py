class Logger(object):
    def __init__(self, default_lineage, updated_lineage=None):
        self.default_lineage= default_lineage

    def update(self, updated_lineage):
        self.updated_lineage= updated_lineage


    def __repr__(self):
        return self.updated_lineage

class Update(object):
    def __init__(self):
        self.taxon= taxon
        self.previous_rank= previous_rank
        self.current_rank= current_rank


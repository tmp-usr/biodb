from setuptools import setup

setup(
      name             = 'biodb',
      version          = '0.1.0',
      description      = 'Functional and taxonomic databases for households.',
      long_description = open('README.md').read(),
      license          = 'MIT',
      url              = 'http://github.com/tmp-usr/biodb/',
      author           = 'Kemal Sanli',
      author_email     = 'kemalsanli1@gmail.com',
      classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics'],
      packages         = ['biodb', 
                          'biodb/parsing',
                          'biodb/downloading',
                          'biodb/sqling',
                          ],
     
      include_package_data = True,
      package_data = {'biodb': [
                          'data/*.txt',
                          'data/db/pacfm.db',
                          'data/downloaded/*.txt',
                          'data/downloaded/kegg_orthology/*.txt',
                          'data/downloaded/kegg_modules/*.txt',
                          'data/downloaded/cog/*.txt',
                          'data/downloaded/pfam/*.txt',
                          'data/downloaded/tigrfams/*.txt',
                          'data/dumps/*.dmp',
                          'data/tmp/*.txt'          
          ] } ,      
      install_requires = ['storm'],
)

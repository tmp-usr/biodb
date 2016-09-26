import os
import shutil
from datetime import datetime

import wget

class Logger(object):
    def __init__(self, db_name, url, description, date, local_path):
        self.db_name= db_name
        self.url = url
        self.description = description
        self.date= date
        self.local_path = local_path

    def __str__(self): return  "%s database %s file was downloaded on %s from the url %s.\n" % (self.db_name, self.description,  self.date, self.url)



class Downloader(object):
    def __init__(self, url, db_path,  protocol):
        self.url= url
        self.protocol= protocol
        self.db_path= db_path

    def download(self):
        if self.protocol == "ftp":
            pass

        elif self.protocol == "http":
            """
            takes too long time! try alternatives!!!
            """
            filename= wget.download(self.url)
            shutil.move(filename, self.db_path)
        

class Manager(object):
    def __init__(self, db_name, download_dir, protocol, urls):
        self.db_name= db_name
        self.download_dir= download_dir
        self.urls= urls
        self.protocol= protocol

        self.loggers=[]

        log_path=os.path.join(download_dir, 'log.txt')
        self.log= open(log_path,'a')         
        
    def get_logger(self, description):
        for logger in self.loggers:
            if logger.description == description:
                return logger

    def build_dirs(self):
        self.db_dir= os.path.join(self.download_dir, self.db_name)
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

    def download(self):
        self.build_dirs()
        for desc, url in self.urls.iteritems():
            local_path= os.path.join(self.db_dir,'%s.txt' %desc)
            if not os.path.exists(local_path):
                d=Downloader(url, local_path, self.protocol)
                d.download()
            
            l= Logger(self.db_name, url, desc, datetime.now().date().isoformat(), local_path)
            self.loggers.append(l)

            self.log.write(str(l))

        

'''
Created on 29 jan 2012

@author: Batch
'''
from file import File

class Search(object):
    def __init__(self, data):
        stats = data['stats']
        self.error = stats['error']
        self.query_changed = stats['query_changed']
        self.time = stats['time']
        self.total_found = stats['total_found']
        self.words = stats['words']

        if self.total_found > 0:
            files_data = data['files']
            self.files = []
            for file_data in files_data:
                self.files.append(File(file_data))
        else:
            self.files = []

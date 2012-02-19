'''
Created on 29 jan 2012

@author: Batch
'''

class MyClass(object):
    '''
    classdocs
    '''

    def __init__(self, data):
        #id
        try:
            self.id = data['id']  
        except:
            self.id = None 
        
        #name
        try:
            self.name = data['name']  
        except:
            self.name = None 
        
        #id_labels - (optional) id of parent label
        try:
            self.id_labels = data['id_labels']  
        except:
            self.id_labels = None 
        
        #sorder - sort order, signed integer
        try:
            self.sorder = data['sorder']  
        except:
            self.sorder = None 

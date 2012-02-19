'''
Created on 29 jan 2012

@author: Batch
'''

class T_File(object):
    def __init__(self, data):
        #name - name
        try:
            self.name = data['name']   
        except:
            self.name = None 
        
        #path - relative file path
        try:
            self.path = data['path']  
        except:
            self.path = None 
        
        #size - size
        try:
            self.size = data['size']  
        except:
            self.size = None 
        
        #ct - content type
        try:
            self.ct = data['ct']  
        except:
            self.ct = None 
        
        #url_dl - direct download link for single file
        try:
            self.url_dl = data['url_dl']  
        except:
            self.url_dl = None 
        

'''
Created on 29 jan 2012

@author: Batch
'''

class Torrent(object):
    '''
    The purpose of this object is only for quering download states. Once a torrent is finished 
    a new file object is created but the torrent object will be keeped till the file is deleted.
    '''
    
    def __init__(self, data):
        #id - id
        try:
            self.id = data['id']  
        except:
            self.id = None 
        
        #name - name
        try:
            self.name = data['name']  
        except:
            self.name = None 
        
        #size - size
        try:
            self.size = data['size']  
        except:
            self.size = None 
        
        #dl_status - enum('active','finished','failed'); state of downloading from BitTorrent 
        try:
            self.dl_status = data['dl_status']  
        except:
            self.dl_status = None 
        
        #active_status - enum('enqueueing','leeching','seeding'); sub status of dl_status='active'; To check if a torrent is ready for your user check for dl_status='finished'
        try:
            self.active_status = data['active_status']  
        except:
            self.active_status = None 
        
        #fail_reason - if dl_status='failed' then this property will contain error message. It's safe to shows this error to your user.
        try:
            self.fail_reason = data['fail_reason']  
        except:
            self.fail_reason = None 
        
        #info_hash - hex(info_hash)
        try:
            self.info_hash = data['info_hash']  
        except:
            self.info_hash = None 
        
        #speed - speed of leeching
        try:
            self.speed = data['speed']  
        except:
            self.speed = None 
        
        #bytes - how many bytes has been downloaded (might be higher then actual size)
        try:
            self.bytes = data['bytes']  
        except:
            self.bytes = None 
        
        #up_speed - speed of seeding
        try:
            self.up_speed = data['up_speed']  
        except:
            self.up_speed = None 
        
        #up_bytes - how many bytes has been uploaded
        try:
            self.up_bytes = data['up_bytes']  
        except:
            self.up_bytes = None 
        
        #have - how many % of torrent has been downloaded
        try:
            self.have = data['have']  
        except:
            self.have = None 
        
        #avail - how many % of torrent is available in swarm. If less then 100% then the torrent may stuck. If now bytes is downloaded in 24h a torrent is auto deleted, if it doesn't start in 12h (i.e. have=0) then it's deleted
        try:
            self.avail = data['avail']  
        except:
            self.avail = None 
        
        #start_dt - when torrent was added/started
        try:
            self.start_dt = data['start_dt']  
        except:
            self.start_dt = None 
        
        #finish_dt - when torrent was finished
        try:
            self.finish_dt = data['finish_dt']  
        except:
            self.finish_dt = None 
        
        #url_page - url to torrent/file info page (optional, returned only by get_tors)
        try:
            self.url_page = data['url_page']  
        except:
            self.url_page = None 

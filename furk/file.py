'''
Created on 29 jan 2012

@author: Batch
'''

class File(object):
    '''
    either a single file or a group of files (in case it was uploaded from BitTorrent). 
    If it's a group of files then it can be downloaded as a single .zip file. 
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
        
        #ctime - datetime when file was added
        try:
            self.ctime = data['ctime']
        except:
            self.ctime = None   
        
        #size - size in bytes
        try:
            self.size = data['size']
        except:
            self.size = None   
        
        #is_ready - '1' if file is http ready. '0' if file was downloaded from BitTorrent and deletedlater for some reason (ex. no downloads in 90 days).
        try:
            self.is_ready = data['is_ready']  
        except:
            self.is_ready = None     
        
        #type - enum('default', 'audio', 'video'), type of file
        try:
            self.type = data['type']
        except:
            self.type = None   

        #status - 'fake' if a fake torrent was detected (mostly video torrents)
        try:
            self.status = data['status']
        except:
            self.status = None   
        
        #info_hash - hex(info_hash)
        try:
            self.info_hash = data['info_hash']  
        except:
            self.info_hash = None   
        
        #video_info - video codec info, output of `ffmpeg - i `
        try:
            self.video_info = data['video_info']
        except:
            self.video_info = None   

        #ss_num - number of screenshots, either 0 or 9
        try:
            self.ss_num = data['ss_num']
        except:
            self.ss_num = None   
        
        #ss_width - screenshot width, always 300
        try:
            self.ss_width = data['ss_width']
        except:
            self.ss_width = None   
        
        #ss_height - screenshot height, vary
        try:
            self.ss_height = data['ss_height']
        except:
            self.ss_height = None   
        
        #ss_urls - array of screenshots
        try:
            self.ss_urls = data['ss_urls']
        except:
            self.ss_urls = None   
        
        #ss_urls_tn - array of screenshots thumbnails
        try:
            self.ss_urls_tn = data['ss_urls_tn'] 
        except:
            self.ss_urls_tn = None   
        
        #av_result - enum('ok', 'warning', 'infected', 'error'), 'ok' if no viruses, 'warning' if a password protected archive was found, 'error' if there's was an internal error while checking (ex. Kaspersky segfaults often)
        try:
            self.av_result = data['av_result']
        except:
            self.av_result = None   
        
        #av_info - last line output of Kaspersky scan
        try:
            self.av_info = data['av_info']
        except:
            self.av_info = None   
        
        #url_page - url to page with detailed info
        try:
            self.url_page = data['url_page']
        except:
            self.url_page = None   
        
        #url_dl - the main direct download link. Link will contain your id and you sub user id. Each your user should get personal links. Don't use one link for more the one user.
        try:
            self.url_dl = data['url_dl']
        except:
            self.url_dl = None
            
        #url_pls - VLC playlist url with direct links inside the playlist
        try:
            self.url_pls = data['url_pls']
        except:
            self.url_pls = None   
        
        #t_files - array of t_files objects, will be included only if 't_files=1' was specified in query and only if id / info_hash params is not an array (i.e. single), don't use if not required, if there's more then 1k of t_files then only first 1k will be included
        try:
            self.t_files = data['t_files']
        except:
            self.t_files = None   
        
        #ids_labels - array of labels ids
        try:
            self.ids_labels = data['ids_labels']
        except:
            self.ids_labels = None   
        
        #notes - created by user text notes about the file
        try:
            self.notes = data['notes']
        except:
            self.notes = None   
            
        #???   
        try:
            self.ss_urls_tn_all = data['ss_urls_tn_all']
        except:
            self.ss_urls_tn_all = None   

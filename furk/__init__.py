'''
Created on 28 jan 2012

@author: Niklas
'''
import urllib2, urllib
import json
from search import Search
from file import File
import cookielib

API_URL = "http://api.furk.net"

class FurkAPI(object):

    def __init__(self, cooke_file):
        self.cooke_file = cooke_file
        
    #search for torrents
    def search(self, query, filter="all", limit="25", match="all",
               moderated="no", offset="0", sort="cached"):
        params = {"q": query, "filter": filter, "match": match,
                  "moderated": moderated, "offset": offset, "sort": sort}
        #"limit" argument does not seem to work
        command = "/api/plugins/metasearch"
        response = self._api_call(command, params)
        if self._status_ok(response):
            return Search(response)
        else:
            return None
        
    #add download (a torrent for example)
    def dl_add(self):
        print "Not yet implemented"
        
    #get linked downloads
    def dl_get(self):
        print "Not yet implemented"
        
    #get files basic info
    def file_info(self):
        print "Not yet implemented"
    
    #get files
    def file_get(self, id="", link_dt_gt="", type="", src="",
               tag="", offset="", sort_col="", sort_type="", name_like=""):
        params = {"id": id, "link_dt_gt": link_dt_gt, "type": type,
                  "src": src, "tag": tag, "offset": offset, "sort_col": sort_col,
                  "sort_type": sort_type, "name_like": name_like}
        #"limit" argument does not seem to work
        command = "/api/file/get"
        response = self._api_call(command, params)
        files_data = response['files']
        files = []
        if self._status_ok(response):
            for file_data in files_data:
                files.append(File(file_data))
        return files
      
    #link files
    def file_link(self):
        print "Not yet implemented"
           
    #unlink files
    def file_unlink(self):
        print "Not yet implemented"
            
    #edit link (file) properties
    def file_update_link(self):
        print "Not yet implemented"
            
    #unlink download
    def dl_unlink(self):
        print "Not yet implemented"
           
    #ping furk
    def ping(self):
        print "Not yet implemented"
            
    #get label
    def label_get(self):
        print "Not yet implemented"
            
    #upsert label
    def label_upsert(self):
        print "Not yet implemented"
            
    #link a label with a file
    def label_link(self):
        print "Not yet implemented"
           
    #unlink a label with a file
    def label_unlink(self):
        print "Not yet implemented"
        
    #login at Furk.net
    def login(self, username, password):
        params = {"login": username, "pwd": password}
        command = "/api/login/login"
        response = self._api_call(command, params)
        
        if self._status_ok(response):
            return True
        else:
            return False
    
    #register at Furk.net
    def reg(self, login, pwd, re_pwd, email):
        params = {"login": login, "pwd": pwd, 're_pwd': re_pwd, 'email': email}
        command = "/api/login/reg"
        response = self._api_call(command, params)
        return response
     
    #logout from Furk.net
    def logout(self):
        print "Not yet implemented"
     
    #send password recovery link
    def recover(self):
        print "Not yet implemented"
     
    #save new password using password recovery link
    def save_pwd(self):
        print "Not yet implemented"
     
    #email verification
    def email_ver(self):
        print "Not yet implemented"

    def _status_ok(self, data):
        status = data['status']
        if status == 'ok':
            return True
        else:
            return False

    def _api_call(self, command, params):
        url = "%s%s?" % (API_URL, command) 
        body = self._get_url(url, params)
        data = json.loads(body)
        print data
        return data

    def _get_url(self, url, params=None):
        url = url + '?INVITE=1464627'
        params['INVITE'] = '1464627'
        if params:
            paramsenc = urllib.urlencode(params)
            req = urllib2.Request(url, paramsenc)
        else:
            req = urllib2.Request(url)
      
        if self.cooke_file:
            cj = cookielib.LWPCookieJar()
            try:
                cj.load(self.cooke_file, ignore_discard=True)
            except:
                print "Could not load cookie jar file."
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            response = opener.open(req)
            cj.save(self.cooke_file, ignore_discard=True)
        else:
            response = urllib2.urlopen(req)
        body = response.read()
        response.close()
        print body
        return body

'''
Created on 14 jan 2012

@author: Batch
'''
import  urllib2
import re
from common import regex_from_to, get_url

API_KEY = '1b0d3c6ac6a6c0fa87b55a1069d6c9c8'

class TMDBInfo(object):
    def __init__(self, movie_name=None, imdb_id=None):
        self.api_key = API_KEY
        if imdb_id:
            self.imdb_id = imdb_id
        else:
            search_url = 'http://api.themoviedb.org/2.1/Movie.search/en/xml/' + self.api_key + '/' + urllib2.quote(movie_name)
            search_result = get_url(search_url)
            self.imdb_id = regex_from_to(search_result, '<id>', '</id>')
        info_url = 'http://api.themoviedb.org/2.1/Movie.imdbLookup/en/xml/' + self.api_key + '/' + self.imdb_id
        self.info_result = get_url(info_url)
        
    def popularity(self):
        return self.getElement('popularity')
    
    def translated(self):
        return self.getElement('translated')
    
    def adult(self):
        return self.getElement('adult')

    def language(self):
        return self.getElement('language')

    def original_name(self):
        return self.getElement('original_name')

    def name(self):
        return self.getElement('name')

    def alternative_name(self):
        return self.getElement('alternative_name')

    def type(self):
        return self.getElement('type')
    
    def id(self):
        return self.getElement('id')
    
    def imdb_id(self):
        return self.getElement('imdb_id')
    
    def url(self):
        return self.getElement('url')

    def overview(self):
        return self.getElement('overview')

    def votes(self):
        return self.getElement('votes')

    def rating(self):
        return self.getElement('rating')

    def tagline(self):
        return self.getElement('tagline')

    def certification(self):
        return self.getElement('certification')

    def released(self):
        return self.getElement('released')

    def runtime(self):
        return self.getElement('runtime')
    
    def budget(self):
        return self.getElement('budget')
    
    def revenue(self):
        return self.getElement('revenue')
    
    def homepage(self):
        return self.getElement('homepage')
    
    def trailer(self):
        return self.getElement('trailer')
    
    def categories(self):
        text = self.getElement('categories')
        r = re.findall("(?i)<category type=\"genre\" name=\"([\S\s]+?)\" url=\"", text)
        
        return r
    
    def keywords(self):
        return self.getElement('keywords')
    
    def studios(self):
        return self.getElement('studios')
    
    def languages_spoken(self):
        return self.getElement('languages_spoken')
    
    def countries(self):
        return self.getElement('countries')
    
    def images(self):
        text = self.getElement('images')        
        r = re.findall("(?i)(?i)<image type=\"([\S\s]+?)\" url=\"([\S\s]+?)\" size=\"([\S\s]+?)\" width=\"([\S\s]+?)\" height=\"([\S\s]+?)\" id=\"([\S\s]+?)\"/>", text)

        images = []
        for type, url, size, width, height, id in r:
            images.append({'type': type, 'url': url, 'size': size, 'width': width, 'height': height, 'id': id})
            
        return images
    
    def cast(self):
        return self.getElement('cast')
    
    def version(self):
        return self.getElement('version')
    
    def last_modified_at(self):
        return self.getElement('last_modified_at')
    
    def getElement(self, element):
        try:
            return regex_from_to(self.info_result, '<' + element + '>', '</' + element + '>')
        except:
            return ""

'''
Created on 10 feb 2012

@author: Batch
'''

import  urllib2
import re
from common import regex_from_to, get_url, regex_get_all

API_KEY = '63AFB061FABE358C'

class TheTVDBInfo(object):
    def __init__(self, imdb_id):
        self.api_key = API_KEY
        self.imdb_id = imdb_id
        info_url = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s&language=en' % (self.imdb_id)
        self.info_result = get_url(info_url)
        if len(self.id()) > 0:
            complete_info_url = 'http://thetvdb.com/api/%s/series/%s/all/en.xml' % (API_KEY, self.id())
            self.info_result = get_url(complete_info_url)
        else:
            self.info_result = ''
    
    def id(self):
        return self.getElement('id')
    
    def Actors(self):
        return self.getElement('Actors')
    
    def Airs_DayOfWeek(self):
        return self.getElement('Airs_DayOfWeek')
    
    def Airs_Time(self):
        return self.getElement('Airs_Time')
    
    def ContentRating(self):
        return self.getElement('ContentRating')
    
    def FirstAired(self):
        return self.getElement('FirstAired')
    
    def Genre(self):
        return self.getElement('Genre')
    
    def IMDB_ID(self):
        return self.getElement('IMDB_ID')
    
    def Language(self):
        return self.getElement('Language')
    
    def Network(self):
        return self.getElement('Network')
    
    def NetworkID(self):
        return self.getElement('NetworkID')
    
    def Overview(self):
        return self.getElement('Overview')
    
    def Rating(self):
        return self.getElement('Rating')
    
    def RatingCount(self):
        return self.getElement('RatingCount')
    
    def Runtime(self):
        return self.getElement('Runtime')
    
    def SeriesID(self):
        return self.getElement('SeriesID')
    
    def SeriesName(self):
        return self.getElement('SeriesName')
    
    def Status(self):
        return self.getElement('Status')
    
    def added(self):
        return self.getElement('added')
    
    def addedBy(self):
        return self.getElement('addedBy')
    
    def banner(self):
        return self.getElement('banner')
    
    def fanart(self):
        return self.getElement('fanart')
    
    def lastupdated(self):
        return self.getElement('lastupdated')
    
    def poster(self):
        return self.getElement('poster')
    
    def zap2it_id(self):
        return self.getElement('zap2it_id')
    
    def episodes(self):
        episodes = []
        episodes_info = regex_get_all(self.info_result, '<Episode>', '</Episode>')
        for episode_info in episodes_info:
            episodes.append(TheTVDBEpisode(episode_info))
        return episodes
    
    def getElement(self, element):
        try:
            return regex_from_to(self.info_result, '<' + element + '>', '</' + element + '>')
        except:
            return ""
        
class TheTVDBEpisode(object):
    def __init__(self, episode_info):
        self.episode_info = episode_info
        
    def id(self):
        return self.getElement('id')
      
    def Combined_episodenumber(self):
        return self.getElement('Combined_episodenumber')
      
    def Combined_season(self):
        return self.getElement('Combined_season')
      
    def DVD_chapter(self):
        return self.getElement('DVD_chapter')
      
    def DVD_discid(self):
        return self.getElement('DVD_discid')
      
    def DVD_episodenumber(self):
        return self.getElement('DVD_episodenumber')
      
    def DVD_season(self):
        return self.getElement('DVD_season')
      
    def Director(self):
        return self.getElement('Director')
      
    def EpImgFlag(self):
        return self.getElement('EpImgFlag')
      
    def EpisodeName(self):
        return self.getElement('EpisodeName')
      
    def EpisodeNumber(self):
        return self.getElement('EpisodeNumber')
      
    def FirstAired(self):
        return self.getElement('FirstAired')
      
    def GuestStars(self):
        return self.getElement('GuestStars')
      
    def IMDB_ID(self):
        return self.getElement('IMDB_ID')
      
    def Language(self):
        return self.getElement('Language')
      
    def Overview(self):
        return self.getElement('Overview')
      
    def ProductionCode(self):
        return self.getElement('ProductionCode')
      
    def Rating(self):
        return self.getElement('Rating')
      
    def RatingCount(self):
        return self.getElement('RatingCount')
      
    def SeasonNumber(self):
        return self.getElement('SeasonNumber')
      
    def Writer(self):
        return self.getElement('Writer')
      
    def absolute_number(self):
        return self.getElement('absolute_number')
  
    def airsafter_season(self):
        return self.getElement('airsafter_season')
  
    def airsbefore_episode(self):
        return self.getElement('airsbefore_episode')
  
    def airsbefore_season(self):
        return self.getElement('airsbefore_season')
  
    def filename(self):
        return self.getElement('filename')
  
    def lastupdated(self):
        return self.getElement('lastupdated')
      
    def seasonid(self):
        return self.getElement('seasonid')
      
    def seriesid(self):
        return self.getElement('seriesid')

    def getElement(self, element):
        try:
            return regex_from_to(self.episode_info, '<' + element + '>', '</' + element + '>')
        except:
            return ""
        
'''
info = TheTVDBInfo('tt0898266')
episodes = info.episodes()
from datetime import date, timedelta

for episode in episodes:
    first_aired = episode.FirstAired()
    if len(episode.FirstAired()) > 0:
        d = episode.FirstAired().split('-')
        episode_date = date(int(d[0]), int(d[1]), int(d[2]))
        if date.today() > episode_date:
            print episode.EpisodeName()
            print episode.FirstAired()
            print "%.2dx%.2d" % (int(episode.SeasonNumber()), int(episode.EpisodeNumber()))
        
url = 'http://thetvdb.com/banners/'
print info.Genre()
print url + info.banner()
print url + info.fanart()
print url + info.poster()
'''

'''
Created on 26 jan 2012

@author: Niklas
'''
import xbmc, xbmcplugin, xbmcgui
import os, sys, time
import urllib
from threading import Thread
from common import notification, wait

WAITING_TIME = 5

def download(url, path, dp=None):
    if os.path.isfile(path) is True:
        return False
    try: 
        if not dp:
            urllib.urlretrieve(url, path)
        else:
            start_time = time.time() 
            urllib.urlretrieve(url, path, lambda nb, bs, fs: _pbhook(nb, bs, fs, dp, start_time)) 
    except:
        while os.path.exists(path): 
            try: 
                os.remove(path) 
                break 
            except: 
                pass 
        
        if sys.exc_info()[0] in (urllib.ContentTooShortError, StopDownloading, OSError): 
            return False
        else: 
            raise 
    return True
         
def download_and_play(name, url, path):
    if os.path.isfile(path) is True:
        notification('download Alert', 'The video you are trying to download already exists!')
        return False
    else:
        print 'attempting to download and play file'
        try:
            print "Starting download Thread"
            dlThread = DownloadAndPlayThread(url, path, name)
            dlThread.start()
            wait(WAITING_TIME, "Buffering")
            xbmc.Player().play(path)
        except:
            print 'download failed'

def play(name, url, list_item=None):
    print 'attempting to stream file'

    if xbmc.Player().isPlayingVideo() == True:
        xbmc.Player().stop()
    if not list_item: 
        list_item = xbmcgui.ListItem(name, iconImage="DefaultVideoBig.png", thumbnailImage='', path=url)
    try:
        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, list_item)
    except:
        print 'file streaming failed'
        notification("Streaming failed", "Streaming failed")

def set_resolved_url(handle, name, url, list_item=None):
    if xbmc.Player().isPlayingVideo() == True:
        xbmc.Player().stop()
    if not list_item: 
        list_item = xbmcgui.ListItem(name, iconImage="DefaultVideoBig.png", thumbnailImage='', path=url)
    list_item.setProperty("IsPlayable", "true")
    xbmcplugin.setResolvedUrl(handle, True, list_item)

def _pbhook(numblocks, blocksize, filesize, dp, start_time):
    try: 
        percent = min(numblocks * blocksize * 100 / filesize, 100) 
        currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
        kbps_speed = numblocks * blocksize / (time.time() - start_time) 
        if kbps_speed > 0: 
            eta = (filesize - numblocks * blocksize) / kbps_speed 
        else: 
            eta = 0 
        kbps_speed = kbps_speed / 1024 
        total = float(filesize) / (1024 * 1024) 
        mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
        e = 'Speed: %.02f Kb/s ' % kbps_speed 
        e += 'ETA: %02d:%02d' % divmod(eta, 60) 
        dp.update(percent, mbs, e)
    except: 
        percent = 100 
        dp.update(percent) 
    if dp.iscanceled(): 
        dp.close() 
        raise StopDownloading('Stopped Downloading')

class StopDownloading(Exception): 
    def __init__(self, value): 
        self.value = value 
    def __str__(self): 
        return repr(self.value)

class DownloadAndPlayThread(Thread):
    def __init__(self, url, path, name):
        self.url = url
        self.path = path
        self.name = name
        self.dialog = None

        Thread.__init__(self) 

    def run(self):
        #get settings
        start_time = time.time() 

        try: 
            urllib.urlretrieve(self.url, self.path, lambda nb, bs, fs: self._dlhook(nb, bs, fs, self, start_time)) 
        except:
            while os.path.exists(self.path): 
                try: 
                    os.remove(self.path) 
                    break 
                except: 
                    pass 

            if sys.exc_info()[0] in (urllib.ContentTooShortError, StopDownloading, OSError): 
                xbmcgui.Dialog().ok('download Canceled!', self.name, 'was canceled')
                return 'false' 
            else: 
                raise 

        return 'downloaded'

    def _dlhook(self, numblocks, blocksize, filesize, dt, start_time):
        print str(numblocks) + " " + str(blocksize) + " " + str(filesize)
        if time.time() > start_time + WAITING_TIME + 5:
            if xbmc.Player().isPlayingVideo() == False:
                print "Stopped playing, stopping download"   
                raise StopDownloading('Stopped Downloading')

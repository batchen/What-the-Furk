'''
Created on 6 feb 2012

@author: Batch
'''

import xbmc, xbmcaddon, xbmcgui, xbmcplugin
from common import notification, get_url, regex_get_all, regex_from_to, create_directory, write_to_file, read_from_file, clean_file_name
from datetime import date, timedelta
import urllib, os, sys, re
import shutil
from furk import FurkAPI
from mediahandler import play, download, download_and_play, set_resolved_url
from meta import TheTVDBInfo, set_movie_meta, download_movie_meta, set_tv_show_meta, download_tv_show_meta, meta_exist
from threading import Thread

ADDON = xbmcaddon.Addon(id='plugin.video.whatthefurk')
DATA_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.whatthefurk'), '')
CACHE_PATH = create_directory(DATA_PATH, "cache")
COOKIE_JAR = os.path.join(DATA_PATH, "cookiejar.lwp")
SUBSCRIPTION_FILE = os.path.join(DATA_PATH, "subsciption.list")
SEARCH_FILE = os.path.join(DATA_PATH, "search.list")
DOWNLOAD_PATH = create_directory(DATA_PATH, "download")
META_PATH = create_directory(DATA_PATH, "meta")
FURK_FILTER = 'cached'
IMDB_TITLE_SEARCH = "http://m.imdb.com/search/title?"
COUNT = "100" #Max 100
HAS = "asin-dvd-us" #To only show movies released on DVD
PRODUCTION_STATUS = "released"
SORT = "user_rating" #alpha/user_rating/num_votes/year/release_date_us/boxoffice_gross_us/moviemeter,desc
VIEW = "simple"

if ADDON.getSetting('release_date') == "true":
    try:
        from_date = ADDON.getSetting('release_date_from')
        to_date = ADDON.getSetting('release_date_to')
        RELEASE_DATE = "%s,%s" (from_date, to_date)
    except:
        RELEASE_DATE = ","
else:
    RELEASE_DATE = ","

if ADDON.getSetting('user_rating') == "true":
    try:
        rating_min = ADDON.getSetting('user_rating_min')
        rating_max = ADDON.getSetting('user_rating_max')
        USER_RATING = "%s,%s" (rating_min, rating_max)
    except:
        USER_RATING = ","
else:
    USER_RATING = ","
    
if ADDON.getSetting('number_of_votes') == "true":
    try:
        votes_min = ADDON.getSetting('number_of_votes_min')
        votes_max = ADDON.getSetting('number_of_votes_max')
        NUM_VOTES = "%s,%s" (votes_min, votes_max)
    except:
        NUM_VOTES = "10000,"
else:
    NUM_VOTES = "10000,"

IMDB_RESULTS = (int(ADDON.getSetting('number_of_results')) + 1) * 100

if ADDON.getSetting('furk_account') == "true":
    FURK_ACCOUNT = True
else:
    FURK_ACCOUNT = False

if ADDON.getSetting('library_mode') == "true":
    LIBRARY_MODE = True
else:
    LIBRARY_MODE = False
    
if ADDON.getSetting('use_unicode_indicators') == "true":
    UNICODE_INDICATORS = True
else:
    UNICODE_INDICATORS = False
    
if ADDON.getSetting('download_meta') == "true":
    DOWNLOAD_META = True
else:
    DOWNLOAD_META = False
    
if ADDON.getSetting('movies_custom_directory') == "true":
    MOVIES_PATH = ADDON.getSetting('movies_directory')
else:
    MOVIES_PATH = create_directory(DATA_PATH, "movies")
    
if ADDON.getSetting('tv_shows_custom_directory') == "true":
    TV_SHOWS_PATH = ADDON.getSetting('tv_shows_directory')
else:
    TV_SHOWS_PATH = create_directory(DATA_PATH, "tv shows")
    
if ADDON.getSetting('first_time_startup') == "true":
    FIRST_TIME_STARTUP = True
else:
    FIRST_TIME_STARTUP = False

PLAY_MODE = 'stream'

FURK = FurkAPI(COOKIE_JAR)

def login_at_furk():
    if FURK_ACCOUNT:
        FURK_USER = ADDON.getSetting('furk_user')
        FURK_PASS = ADDON.getSetting('furk_pass')
    else:
        return False
    
    if FURK.login(FURK_USER, FURK_PASS):
        return True
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok("Login failed", "The addon failed to login at Furk.net.", "Make sure you have confirmed your email and your", "login information is entered correctly in addon-settings")
    

def download_meta_zip():
    menu_data = ["",
                  "http://wtf.gosub.dk/low.zip",
                  "http://wtf.gosub.dk/medium.zip",
                  "http://wtf.gosub.dk/high.zip",
                  "http://wtf.gosub.dk/medium.zip"]
    menu_texts = ["Don't download",
                 "Download low quality images [123MB]",
                 "Download mid quality images [210MB]",
                 "Download high quality images [508MB]",
                 "Download maximum quality images [722MB]"]
    data_url = "http://wtf.gosub.dk/data-338438.zip"
    
    dialog = xbmcgui.Dialog() 
    menu_id = dialog.select('Select file', menu_texts)
    if menu_id < 1:
        return
    
    ADDON.setSetting('meta_quality', value=str(menu_id + 1))
    
    try:
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Searching for files')
        
        meta_url = menu_data[menu_id]
        xbmc.log("[What the Furk] Downloading meta...")
        meta_path = os.path.join(DOWNLOAD_PATH, "meta.zip")
        download(meta_url, meta_path, pDialog)
        xbmc.log("[What the Furk] Extracting meta...")
        xbmc.executebuiltin("XBMC.Extract(%s , %s)" % (meta_path, META_PATH))
        xbmc.log("[What the Furk] ...done!")
        data_path = os.path.join(DOWNLOAD_PATH, "data.zip")
        download(data_url, data_path, pDialog)
        xbmc.executebuiltin("XBMC.Extract(%s , %s)" % (data_path, META_PATH))
        xbmc.log("[What the Furk] All done!")
    except:
        dialog.ok("Setup meta data", "Unable to reach the host server.")
    
def register_account():
    keyboard = xbmc.Keyboard('', 'Username')
    keyboard.doModal()
    username = None
    if keyboard.isConfirmed():
        username = keyboard.getText()
    if username == None:
        return False

    password = None
    keyboard = xbmc.Keyboard('', 'Password')
    keyboard.doModal()
    if keyboard.isConfirmed():
        password = keyboard.getText()
    if password == None:
        return False
     
    email = None
    keyboard = xbmc.Keyboard('', 'E-mail')
    keyboard.doModal()
    if keyboard.isConfirmed():
        email = keyboard.getText()
    if email == None:
        return False
        
    dialog = xbmcgui.Dialog()
    response = FURK.reg(username, password, password, email)
    
    if response['status'] == 'ok':
        ADDON.setSetting('furk_user', value=username)
        ADDON.setSetting('furk_pass', value=password)
        dialog.ok("Registration", "Registration formula completed.", "In order to complete the registration you need to", "click the confirmation link sent to your email.")    
        return True
    else:
        errors = response['errors']
        for key in errors.keys():
            dialog.ok("Registration error", "%s: %s" % (key, errors[key]))
        return register_account()

def get_subscriptions():
    try:
        content = read_from_file(SUBSCRIPTION_FILE)
        lines = content.split('\n')
        
        for line in lines:
            data = line.split('\t')
            if len(data) == 2:
                if data[1].startswith('tt'):
                    tv_show_name = data[0]
                    tv_show_imdb = data[1]
                    tv_show_mode = "strm tv show dialog"
                    create_tv_show_strm_files(tv_show_name, tv_show_imdb, tv_show_mode, TV_SHOWS_PATH)
                else:
                    mode = data[1]
                    items = get_menu_items(name, mode, "", "")
                    
                    for (url, li, isFolder) in items:
                        paramstring = url.replace(sys.argv[0], '')
                        params = get_params(paramstring)
                        movie_name = urllib.unquote_plus(params["name"])
                        movie_data = urllib.unquote_plus(params["name"])
                        movie_imdb = urllib.unquote_plus(params["imdb_id"])
                        movie_mode = "strm movie dialog"
                        create_strm_file(movie_name, movie_data, movie_imdb, movie_mode, MOVIES_PATH)
                    
    except:
        xbmc.log("[What the Furk] Failed to fetch subscription")

def subscription_index(name, mode):
    try:
        content = read_from_file(SUBSCRIPTION_FILE)
        line = str(name) + '\t' + str(mode)
        lines = content.split('\n')
        index = lines.index(line)
        return index
    except:
        return -1 #Not subscribed

def subscribe(name, mode):
    if subscription_index(name, mode) >= 0:
        return
    content = str(name) + '\t' + str(mode) + '\n'
    write_to_file(SUBSCRIPTION_FILE, content, append=True)
    
def unsubscribe(name, mode):
    index = subscription_index(name, mode)
    if index >= 0:
        content = read_from_file(SUBSCRIPTION_FILE)
        lines = content.split('\n')
        lines.pop(index)
        s = ''
        for line in lines:
            if len(line) > 0:
                s = s + line + '\n'
        write_to_file(SUBSCRIPTION_FILE, s)
    
def find_search_query(query):
    try:
        content = read_from_file(SEARCH_FILE) 
        lines = content.split('\n')
        index = lines.index(query)
        return index
    except:
        return -1 #Not found
    
def add_search_query(query):
    if find_search_query(query) >= 0:
        return

    if os.path.isfile(SEARCH_FILE):
        content = read_from_file(SEARCH_FILE)
    else:
        content = ""

    lines = content.split('\n')
    s = '%s\n' % query
    for line in lines:
        if len(line) > 0:
            s = s + line + '\n'
    write_to_file(SEARCH_FILE, s)
    
def remove_search_query(query):
    index = find_search_query(query)
    if index >= 0:
        content = read_from_file(SEARCH_FILE)
        lines = content.split('\n')
        lines.pop(index)
        s = ''
        for line in lines:
            if len(line) > 0:
                s = s + line + '\n'
        write_to_file(SEARCH_FILE, s)
    
def create_strm_file(name, data, imdb_id, mode, dir_path):
    try:
        strm_string = create_url(name, mode, data=data, imdb_id=imdb_id)
        filename = clean_file_name("%s.strm" % name)
        path = os.path.join(dir_path, filename)
        stream_file = open(path, 'w')
        stream_file.write(strm_string)
        stream_file.close()
    except:
        xbmc.log("[What the Furk] Error while creating strm file for : " + name)

def create_tv_show_strm_files(name, imdb_id, mode, dir_path):
    info = TheTVDBInfo(imdb_id)
    episodes = info.episodes()
    
    tv_show_path = create_directory(dir_path, name)
    for episode in episodes:
        first_aired = episode.FirstAired()
        if len(first_aired) > 0:
            d = first_aired.split('-')
            episode_date = date(int(d[0]), int(d[1]), int(d[2]))
            if date.today() > episode_date:
                season_number = int(episode.SeasonNumber())
                if season_number > 0:
                    episode_number = int(episode.EpisodeNumber())
                    episode_name = episode.EpisodeName()
                    display = "[S%.2dE%.2d] %s" % (season_number, episode_number, episode_name)
                    data = '%s<|>%s<|>%d<|>%d' % (name, episode_name, season_number, episode_number)
                    season_path = create_directory(tv_show_path, str(season_number))
                    create_strm_file(display, data, imdb_id, mode, season_path)

def remove_strm_file(name, dir_path):
    try:
        filename = "%s.strm" % (clean_file_name(name, use_blanks=False))
        path = os.path.join(dir_path, filename)
        os.remove(path)
    except:
        xbmc.log("[What the Furk] Was unable to remove movie: %s" % (name)) 

def remove_tv_show_strm_files(name, dir_path):
    try:
        path = os.path.join(dir_path, name)
        shutil.rmtree(path) 
    except:
        xbmc.log("[What the Furk] Was unable to remove TV show: %s" % (name)) 
    
def check_sources_xml(path):
    try:
        source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')
        f = open(source_path, 'r')
        content = f.read()
        f.close()
        path = str(path).replace('\\', '\\\\')
        if re.search(path, content):
            return True
    except:
        xbmc.log("[What the Furk] Could not find sources.xml!")   
    return False

def setup_sources():
    xbmc.log("[What the Furk] Trying to add source paths...")
    source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')
    
    try:
        f = open(source_path, 'r')
        content = f.read()
        f.close()
        r = re.search("(?i)(<sources>[\S\s]+?<video>[\S\s]+?>)\s+?(</video>[\S\s]+?</sources>)", content)
        new_content = r.group(1)
        if not check_sources_xml(MOVIES_PATH):
            new_content += '<source><name>Movies (What the Furk)</name><path pathversion="1">'
            new_content += MOVIES_PATH
            new_content += '</path></source>'
        if not check_sources_xml(TV_SHOWS_PATH):
            new_content += '<source><name>TV Shows (What the Furk)</name><path pathversion="1">'
            new_content += TV_SHOWS_PATH
            new_content += '</path></source>'
        new_content += r.group(2)
        
        f = open(source_path, 'w')
        f.write(new_content)
        f.close()

        dialog = xbmcgui.Dialog()
        dialog.ok("Source folders added", "To complete the setup:", " 1) Restart XBMC.", " 2) Set the content type of added sources.")
        #if dialog.yesno("Restart now?", "Do you want to restart XBMC now?"):
            #xbmc.restart()
    except:
        xbmc.log("[What the Furk] Could not edit sources.xml")
        
#Scrape


def search_imdb(params):
    movies = []
    count = 0
    while count < IMDB_RESULTS:
        body = title_search(params, str(count))
        movies.extend(get_imdb_search_result(body))
        count = count + 100
    return movies
    
def title_search(params, start="1"):
    params["count"] = COUNT
    params["has"] = HAS
    params["view"] = VIEW
    params["num_votes"] = NUM_VOTES
    params["user_rating"] = USER_RATING
    params["start"] = start
    url = IMDB_TITLE_SEARCH
    for key in params:
        url += "%s=%s&" % (key, params[key])
    body = get_url(url, cache=CACHE_PATH, cache_time=86400) #Need to clear cache to allow filter changes    
    return body
    
def get_imdb_search_result(body):
    all_tr = regex_get_all(body, '<tr class=', '</tr>')
    
    movies = []
    for tr in all_tr:
        all_td = regex_get_all(tr, '<td', '</td>')
        imdb_id = regex_from_to(all_td[1], '/title/', '/')
        name = regex_from_to(all_td[1], '/">', '</a>')
        year = regex_from_to(all_td[1], '<span class="year_type">\(', '\)')
        rating = regex_from_to(all_td[2], '<b>', '</b>')
        votes = regex_from_to(all_td[3], '\n', '\n')
        movies.append({'imdb_id': imdb_id, 'name': name, 'year': year, 'rating': rating, 'votes': votes})
    return movies            

def scrape_xspf(body):
    all_track = regex_get_all(body, '<track>', '</track>')
    tracks = []
    for track in all_track:
        name = regex_from_to(track, '<title>', '</title>')
        location = regex_from_to(track, '<location>', '</location>')
        tracks.append({'name': name, 'location': location})
    return tracks

def execute_video(name, url, list_item, strm=False):
    if PLAY_MODE == 'stream':
        if strm:
            set_resolved_url(int(sys.argv[1]), name, url) 
        else:
            play(name, url, list_item) 
    elif PLAY_MODE == 'download and play':
        if strm:
            download_and_play(name, url, play=True, handle=int(sys.argv[1]))
        else:
            download_and_play(name, url, play=True)

def get_items_in_dir(path):
    items = []
    for dirpath, dirnames, filenames in os.walk(path): 
        for subdirname in dirnames: 
            items.append(subdirname) 
        for filename in filenames:
            if filename.endswith(".strm"): 
                items.append(filename[:-5])
        
    return items

def exist_in_dir(name, path, isMovie=False):
    if isMovie:
        name = "%s.strm" % name
    item_list = os.listdir(path)
    
    for item in item_list:
        if item == name:
            return True
    return False
    #test = clean_file_name(name)
    #for item in get_items_in_dir(path):
    #    if item == test:
    #        return True
    #return False

#Menu

def setup():
    if FIRST_TIME_STARTUP:
        dialog = xbmcgui.Dialog()
        
        if not FURK_ACCOUNT:
            if dialog.yesno("Setup account", "This addon requires a Furk.net account.", "What do you want to do?", '', "Use existing account", "Create new account"):
                if not register_account():
                    dialog.ok("Setup account", "Account registation aborted.")
                    dialog.ok("Missing information", "You need to write down your Furk.net", "login information in the addon-settings.")    
                    ADDON.openSettings()
            else:
                dialog.ok("Missing information", "You need to write down your Furk.net", "login information in the addon-settings.")    
                ADDON.openSettings()     
        if dialog.yesno("Setup metadata", "This addon supports the use of metadata,", "this data can be pre-downloaded.", "Do you want to download a metadata package?"):
            download_meta_zip()
        if dialog.yesno("Setup metadata", "This addon can download metadata while you", "are browsing movie and TV show categories.", "Do you want to activate this feature?"):
            ADDON.setSetting('download_meta', value='true')
        else:
            ADDON.setSetting('download_meta', value='false')  
        if not check_sources_xml(MOVIES_PATH) or not check_sources_xml(TV_SHOWS_PATH):
            if dialog.yesno("Setup folder", "The directories used are not listed as video sources.", "Do you want to add them to sources.xml now?"):
                setup_sources()
        ADDON.setSetting('first_time_startup', value='false')      
        
def main_menu():
    items = []
    items.append(create_item_tuple('All movies', 'all movies menu', isSubscribable=True))  
    items.append(create_item_tuple('Movies by genre', 'movie genres menu'))  
    items.append(create_item_tuple('New movies', 'new movies menu', isSubscribable=True))
    items.append(create_item_tuple('All TV shows', 'all tv shows menu'))  
    items.append(create_item_tuple('TV shows by genre', 'tv show genres menu'))  
    items.append(create_item_tuple('Active TV shows', 'active tv shows menu'))
    items.append(create_item_tuple('Search', 'search menu'))  
    if LIBRARY_MODE and SUBSCRIPTION_FILE:
        #add_menu_item('Subscriptions', 'subscription menu') 
        items.append(create_item_tuple('Subscriptions', 'subscription menu'))  
    #xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return items

def movies_all_menu():
    params = {}
    params["release_date"] = RELEASE_DATE
    params["sort"] = SORT
    params["title_type"] = "feature,documentary"
    params["production_status"] = PRODUCTION_STATUS
    movies = search_imdb(params)
    return create_movie_items(movies)

def movies_genres_menu():
    items = []
    genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'History', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    for genre in genres:
        items.append(create_item_tuple(genre, 'movie genre menu', isSubscribable=True))
    return items

def movies_genre_menu(genre):
    params = {}
    params["release_date"] = RELEASE_DATE
    params["sort"] = SORT
    params["title_type"] = "feature,documentary"
    params["genres"] = genre
    params["production_status"] = PRODUCTION_STATUS
    movies = search_imdb(params)
    return create_movie_items(movies)

def movies_new_menu():
    d = (date.today() - timedelta(days=365))
    params = {}
    params["release_date"] = "%s," % d
    params["sort"] = "release_date_us,desc"
    params["title_type"] = "feature,documentary"
    params["production_status"] = PRODUCTION_STATUS
    movies = search_imdb(params)
    return create_movie_items(movies)

def tv_shows_all_menu():
    params = {}
    params["release_date"] = RELEASE_DATE
    params["sort"] = SORT
    params["title_type"] = "tv_series"
    params["production_status"] = PRODUCTION_STATUS
    tv_shows = search_imdb(params)
    return create_tv_show_items(tv_shows)

def tv_shows_genres_menu():
    items = []
    genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'History', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    for genre in genres:
        items.append(create_item_tuple(genre, 'tv show genre menu', isSubscribable=True))
    return items

def tv_shows_genre_menu(genre):
    params = {}
    params["release_date"] = RELEASE_DATE
    params["sort"] = SORT
    params["title_type"] = "tv_series"
    params["genres"] = genre
    params["production_status"] = PRODUCTION_STATUS
    tv_shows = search_imdb(params)
    return create_tv_show_items(tv_shows)

def tv_shows_active_menu():
    params = {}
    params["production_status"] = "active"
    params["sort"] = SORT
    params["title_type"] = "tv_series"
    tv_shows = search_imdb(params)
    return create_tv_show_items(tv_shows)

def tv_shows_seasons_menu(name, imdb_id):
    print ""
    
def tv_shows_episodes_menu(name, imdb_id):
    items = []
    info = TheTVDBInfo(imdb_id)
    episodes = info.episodes()
    
    name = name.split('(')[0][:-1]
    
    for episode in episodes:
        first_aired = episode.FirstAired()
        if len(first_aired) > 0:
            d = first_aired.split('-')
            episode_date = date(int(d[0]), int(d[1]), int(d[2]))
            if date.today() > episode_date:
                season_number = int(episode.SeasonNumber())
                if season_number > 0:
                    episode_number = int(episode.EpisodeNumber())
                    episode_name = episode.EpisodeName()
                    cleaned_name = clean_file_name(episode_name, use_blanks=False)
                    display = "(S%.2dE%.2d) %s" % (season_number, episode_number, cleaned_name)
                    data = "%s<|>%s<|>%d<|>%d" % (name, episode_name, season_number, episode_number)
                    (url, li, isFolder) = create_item_tuple(display, 'episode dialog', data=data, imdb_id=imdb_id)
                    li = set_tv_show_meta(li, imdb_id, META_PATH)
                    li.setInfo('video', {'title': display})
                    items.append((url, li, isFolder)) #items.append((url, li, False))
    return items

def subscription_menu():
    items = []
    s = read_from_file(SUBSCRIPTION_FILE)
    menu_items = s.split('\n')
    
    for menu_item in menu_items:
        if len(menu_item) < 3:
            break
        data = menu_item.split('\t')
        item_name = data[0]
        item_data = data[1]
        items.append(create_item_tuple('%s [%s]' % (item_name, item_data), 'unsubscribe', data=item_data, isFolder=False))

    return items

def search_menu():
    items = []
    items.append(create_item_tuple('@Search...', 'manual search'))
    
    if os.path.isfile(SEARCH_FILE):
        s = read_from_file(SEARCH_FILE)
        search_queries = s.split('\n')
        for query in search_queries:
            items.append(create_item_tuple(query, 'manual search', data=query))

    return items

def manual_search(query):
    if query.startswith('@'):
        query = ''
    
    keyboard = xbmc.Keyboard(query, 'Search')
    keyboard.doModal()

    if keyboard.isConfirmed():
        query = keyboard.getText()
        if len(query) > 0:
            add_search_query(query)
            movie_dialog(query)

def episode_dialog(data, imdb_id=None, strm=False):
    dialog = xbmcgui.Dialog()
    open_playlists = dialog.yesno("Seach alternatives", "What search routine should be done?",
                    "Regular search: Slow, but finds all results.",
                    "Fast search: Fast but finds less files.",
                    "Fast search", "Regular search")
    
    data = data.split('<|>')
    tv_show_name = data[0]
    episode_name = data[1]
    season_number = int(data[2])
    episode_number = int(data[3])

    season_episode = "s%.2de%.2d" % (season_number, episode_number)
    season_episode2 = "%d%.2d" % (season_number, episode_number)

    tv_show_season = "%s season" % (tv_show_name)
    tv_show_episode = "%s %s" % (tv_show_name, season_episode)
    track_filter = [episode_name, season_episode, season_episode2]
    
    files = []
    files.extend(search(tv_show_episode, limit='25'))
    if open_playlists:
        files.extend(search(tv_show_season, limit='10'))
        files.extend(search(tv_show_name, limit='10')) 
    files = remove_list_duplicates(files)
    
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Searching for files')

    tracks = []
    count = 0
    for f in files:
        count = count + 1
        percent = int(float(count * 100) / len(files))
        text = "%s files found" % len(tracks)
        pDialog.update(percent, text)
        if pDialog.iscanceled(): 
            pDialog.close()
            if strm:
                set_resolved_to_dummy()
            return
        if f.av_result == "ok" and f.type == "video":
            new_tracks = filter_playlist_tracks(get_playlist_tracks(f, open_playlists=open_playlists), track_filter)
            tracks.extend(new_tracks)
    pDialog.close()
    (url, name) = track_dialog(tracks)
    
    if not url or not name:
        if strm:
            set_resolved_to_dummy()
        return
    
    li = xbmcgui.ListItem(clean_file_name(episode_name))
    li = set_tv_show_meta(li, imdb_id, META_PATH)
    execute_video(name, url, li, strm)

def movie_dialog(data, imdb_id=None, strm=False):
    dialog = xbmcgui.Dialog()
    open_playlists = dialog.yesno("Seach alternatives", "What search routine should be done?",
                    "Regular search: Slow, but finds all results.",
                    "Fast search: Fast but finds less files.",
                    "Fast search", "Regular search")
    
    files = search(data, limit='25')

    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Searching for files')
        
    tracks = []
    count = 0
    for f in files:
        count = count + 1
        percent = int(float(count * 100) / len(files))
        text = "%s files found" % len(tracks)
        pDialog.update(percent, text)
        if f.type == "video":
            new_tracks = get_playlist_tracks(f, open_playlists=open_playlists)
            tracks.extend(new_tracks)

    (url, name) = track_dialog(tracks)
    
    if not url or not name:
        if strm:
            set_resolved_to_dummy()
        return
    
    li = xbmcgui.ListItem(clean_file_name(data))
    li = set_movie_meta(li, imdb_id, META_PATH)
    execute_video(name, url, li, strm)

def set_resolved_to_dummy():
    DUMMY_PATH = os.path.join(ADDON.getAddonInfo('path'), 'dummy.wma')
    listitem = xbmcgui.ListItem('Dummy data to avoid error message', path=DUMMY_PATH)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

def track_dialog(tracks):
    menu_texts = []
    menu_data = []
    for track in tracks:
        name = track['name']
        if  name.find('.VOB') < 0:
            menu_texts.append(name)
            menu_data.append(track['location'])
    
    dialog = xbmcgui.Dialog() 
    
    if len(menu_data) == 0:
        dialog = xbmcgui.Dialog()
        dialog.ok("No files found", "The search was not able to find any files.")
        return (None, None)
    
    menu_id = dialog.select('Select file', menu_texts)
    
    if(menu_id < 0):
        return (None, None)
    
    url = menu_data[menu_id]
    name = menu_texts[menu_id]
    return (url, name)

def search(query, limit=25):
    query = clean_file_name(query)
    query = query.replace('\'', ' ')

    if not login_at_furk():
        return []
    
    files = []
    if type(query).__name__ == 'list':
        for q in query:
            search_result = FURK.search(q, filter=FURK_FILTER, limit=limit)
            if search_result.query_changed == None:
                files.extend(search_result.files)
    else:
        search_result = FURK.search(query, filter=FURK_FILTER, limit=limit)
        if search_result.query_changed == None:
            files = search_result.files
    return files

def remove_list_duplicates(list_to_check): 
    temp_set = {} 
    map(temp_set.__setitem__, list_to_check, []) 
    return temp_set.keys()

def filter_playlist_tracks(tracks, track_filters):
    r = []
    if type(track_filters).__name__ == 'list':
        for track in tracks:
            name = make_string_comparable(track['name'])
            for f in track_filters:
                track_filter = make_string_comparable(f)
                if name.find(track_filter) >= 0:
                    r.append(track)
                    break
    else:
        track_filter = make_string_comparable(track_filters)
        for track in tracks:
            name = make_string_comparable(track['name'])
            if name.find(track_filter) >= 0:
                r.append(track)
    return r

def make_string_comparable(s):
    s = s.lower()
    s = ''.join(e for e in s if e.isalnum())
    return s

def get_playlist_tracks(playlist_file, open_playlists=False):
    tracks = []
    try:
        file_name = playlist_file.name
        if file_name.endswith('.avi') or file_name.endswith('.mkv'):
            tracks = [{'name': file_name, 'location': playlist_file.url_dl}]
        elif open_playlists:
            playlist_url = playlist_file.url_pls
            playlist = get_url(playlist_url)
            tracks = scrape_xspf(playlist)
    except:
        pass
    return tracks
 
def create_movie_tuple(name, imdb_id):
    if LIBRARY_MODE:
        return create_item_tuple(name, 'toggle movie strm', data=name, isFolder=False, isMovieItem=True, imdb_id=imdb_id)
    else:
        return create_item_tuple(name, 'movie dialog', isFolder=False, data=name, isMovieItem=True, imdb_id=imdb_id)
        
def create_tv_show_tuple(name, imdb_id):
    if LIBRARY_MODE:
        return create_item_tuple(name, 'toggle tv show strms', data=name, isFolder=False, isTVShowItem=True, isSubscribable=True, imdb_id=imdb_id)
    else:
        return create_item_tuple(name, 'episodes menu', data=name, isTVShowItem=True, isSubscribable=True, imdb_id=imdb_id)
        
def create_item_tuple(name, mode, data="", imdb_id="", isFolder=True, isSubscribable=False, isMovieItem=False, isTVShowItem=False):
    url = create_url(name, mode, data, imdb_id)
    li = create_list_item(name, mode, isSubscribable=isSubscribable, isMovieItem=isMovieItem, isTVShowItem=isTVShowItem, imdb_id=imdb_id)
    if not imdb_id == "":
        if isMovieItem:
            li = set_movie_meta(li, imdb_id, META_PATH)
        if isTVShowItem:
            li = set_tv_show_meta(li, imdb_id, META_PATH)
    return (url, li, isFolder)

def create_url(name, mode, data="", imdb_id=""):
    name = urllib.quote(str(name))
    data = urllib.quote(str(data))
    mode = str(mode)
    url = sys.argv[0] + '?name=%s&data=%s&mode=%s&imdb_id=%s' % (name, data, mode, imdb_id)
    return url

def create_list_item(name, mode, isSubscribable=False, isMovieItem=False, isTVShowItem=False, imdb_id=''):
    contextMenuItems = []
    prefix = "   "
    
    if isMovieItem:
        contextMenuItems.append(('Movie Information', 'XBMC.Action(Info)'))
    if isTVShowItem:
        contextMenuItems.append(('TV Show information', 'XBMC.Action(Info)'))

    if LIBRARY_MODE:
        if isMovieItem:
            c_name = clean_file_name(name)
            if exist_in_dir(c_name, MOVIES_PATH, isMovie=True):
                if UNICODE_INDICATORS:
                    prefix = u'\u2605'
                else:
                    prefix = "(A)"
        if isTVShowItem:
            c_name = clean_file_name(name.split('(')[0][:-1])
            if exist_in_dir(c_name, TV_SHOWS_PATH):
                if UNICODE_INDICATORS:
                    prefix = u'\u2605'
                else:
                    prefix = "(A)"
        
        if isTVShowItem:
            sub_data = imdb_id
            sub_path = TV_SHOWS_PATH
        else:
            sub_data = mode
            sub_path = MOVIES_PATH
        if isSubscribable:
            if subscription_index(name, sub_data) < 0:
                subscribe_url = sys.argv[0] + '?name=%s&data=%s&mode=subscribe' % (urllib.quote(name), sub_data)
                contextMenuItems.append(('Subscribe', 'XBMC.RunPlugin(%s)' % subscribe_url))
            else:
                if UNICODE_INDICATORS:
                    prefix = u'\u2665'
                else:
                    prefix = "(S)"
                unsubscribe_url = sys.argv[0] + '?name=%s&data=%s&mode=unsubscribe' % (urllib.quote(name), sub_data)
                contextMenuItems.append(('Unsubscribe', 'XBMC.RunPlugin(%s)' % unsubscribe_url))

    li = xbmcgui.ListItem(prefix + clean_file_name(name, use_blanks=False))
    li.addContextMenuItems(contextMenuItems)
    
    return li

def create_movie_items(movies):
    items = []
    missing_meta = []

    for movie in movies:
        name = "%s (%s)" % (movie['name'], movie['year'])
        imdb_id = movie['imdb_id']
        
        items.append(create_movie_tuple(name, imdb_id))
        if not meta_exist(imdb_id, META_PATH):
            missing_meta.append(imdb_id)
    
    return items, missing_meta

def create_tv_show_items(tv_shows):
    items = []
    missing_meta = []

    for tv_show in tv_shows:
        name = "%s (%s)" % (tv_show['name'], tv_show['year'])
        imdb_id = tv_show['imdb_id']
        items.append(create_tv_show_tuple(name, imdb_id))
        if not meta_exist(imdb_id, META_PATH):
            missing_meta.append(imdb_id)
    
    return items, missing_meta

def scan_library():
    if xbmc.getCondVisibility('Library.IsScanningVideo') == False:           
        #if ADDON.getSetting('update_video') == 'true':
        xbmc.executebuiltin('UpdateLibrary(video)')

def clean_library():
    #if xbmc.getCondVisibility('Library.IsScanningVideo') == False:           
        #if ADDON.getSetting('update_video') == 'true':
    xbmc.executebuiltin('CleanLibrary(video)')

def get_missing_meta(missing_meta, type):
    if len(missing_meta) > 0 and DOWNLOAD_META:
        xbmc.log("[What the Furk] Downloading missing %s meta data for %d files..." % (type, len(missing_meta)))
        dlThread = DownloadThread(missing_meta, type)
        dlThread.start()
        xbmc.log("[What the Furk] ...meta download complete!")
    
class DownloadThread(Thread):
    def __init__(self, missing_meta, meta_type):
        self.missing_meta = missing_meta
        self.type = meta_type
        Thread.__init__(self)

    def run(self):
        if self.type == 'movies':
            for imdb_id in self.missing_meta:
                download_movie_meta(imdb_id, META_PATH)
        if self.type == 'tv shows':
            for imdb_id in self.missing_meta:
                download_tv_show_meta(imdb_id, META_PATH)
        xbmc.executebuiltin("Container.Refresh")

def get_all_meta():
    genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
          'Fantasy', 'History', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    xbmc.log("[What the Furk] Downloading movies_all_menu...")
    items, missing_meta = movies_all_menu()
    for imdb_id in missing_meta:
            download_movie_meta(imdb_id, META_PATH)
    xbmc.log("[What the Furk] ...complete!")
    
    for genre in genres:  
        xbmc.log("[What the Furk] Downloading movies_genre_menu %s..." % genre)
        items, missing_meta = movies_genre_menu(str(genre).lower())
        for imdb_id in missing_meta:
            download_movie_meta(imdb_id, META_PATH)
        xbmc.log("[What the Furk] ...complete!")
        
    xbmc.log("[What the Furk] Downloading movies_new_menu...")
    items, missing_meta = movies_new_menu()
    for imdb_id in missing_meta:
                download_tv_show_meta(imdb_id, META_PATH)
    xbmc.log("[What the Furk] ...complete!")
    
    xbmc.log("[What the Furk] Downloading tv_shows_all_menu...")
    items, missing_meta = tv_shows_all_menu()
    for imdb_id in missing_meta:
                download_tv_show_meta(imdb_id, META_PATH)
    xbmc.log("[What the Furk] ...complete!")
    
    for genre in genres:
        xbmc.log("[What the Furk] Downloading tv_shows_genre_menu %s..." % genre)
        items, missing_meta = tv_shows_genre_menu(str(genre).lower())
        for imdb_id in missing_meta:
                download_tv_show_meta(imdb_id, META_PATH)
        xbmc.log("[What the Furk] ...complete!")
     
    xbmc.log("[What the Furk] Downloading tv_shows_active_menu...")
    items, missing_meta = tv_shows_active_menu()
    for imdb_id in missing_meta:
                download_tv_show_meta(imdb_id, META_PATH)
    xbmc.log("[What the Furk] ...complete!")
    xbmc.log("[What the Furk] META DOWNLOAD COMPLETE!")

def get_menu_items(name, mode, data, imdb_id):
    if mode == "main menu": #Main menu
        items = main_menu()
    elif mode == "all movies menu": #all menu
        items, missing_meta = movies_all_menu()
        get_missing_meta(missing_meta, 'movies')
    elif mode == "movie genres menu": #Genres menu
        items = movies_genres_menu()
    elif mode == "movie genre menu": #Genre menu
        items, missing_meta = movies_genre_menu(str(name).lower())
        get_missing_meta(missing_meta, 'movies')
    elif mode == "new movies menu": #New movies menu
        items, missing_meta = movies_new_menu()
        get_missing_meta(missing_meta, 'movies')
    elif mode == "all tv shows menu": #all menu
        items, missing_meta = tv_shows_all_menu()
        get_missing_meta(missing_meta, 'tv shows')
    elif mode == "tv show genres menu": #Genres menu
        items = tv_shows_genres_menu()
    elif mode == "tv show genre menu": #Genre menu
        items, missing_meta = tv_shows_genre_menu(str(name).lower())
        get_missing_meta(missing_meta, 'tv shows')
    elif mode == "active tv shows menu": #New movies menu
        items, missing_meta = tv_shows_active_menu()
        get_missing_meta(missing_meta, 'tv shows')
    elif mode == "episodes menu":
        items = tv_shows_episodes_menu(name, imdb_id)
    elif mode == "seasons menu":
        items = tv_shows_seasons_menu(name, imdb_id)
    elif mode == "subscription menu": #Subscription menu
        items = subscription_menu()
    elif mode == "search menu": #Search menu
        items = search_menu()
    else:
        items = []
        
    return items

#Other

def get_params(paramstring):
    param = {}
    if len(paramstring) >= 2:
        paramstring = paramstring.replace('?', '')
        pairsofparams = paramstring.split('&')
        for p in pairsofparams:
            splitparams = p.split('=')
            if len(splitparams) == 2:
                param[splitparams[0]] = splitparams[1]            
    return param


params = get_params(sys.argv[2])

try:
    name = urllib.unquote_plus(params["name"])
except:
    name = ""
try:
    data = urllib.unquote_plus(params["data"])
except:
    data = ""
try:
    imdb_id = urllib.unquote_plus(params["imdb_id"])
except:
    imdb_id = ""
try:
    mode = urllib.unquote_plus(params["mode"])
except:
    mode = "main menu"

xbmc.log("[What the Furk] mode=%s     name=%s     data=%s     imdb_id=%s" % (mode, name, data, imdb_id))

if mode.endswith('menu'):
    items = get_menu_items(name, mode, data, imdb_id)
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), items, len(items))
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    setup()
elif mode == "episode dialog":
    episode_dialog(data, imdb_id)
elif mode == "movie dialog":
    movie_dialog(data, imdb_id)
elif mode == "strm movie dialog":
    movie_dialog(data, imdb_id, strm=True)
elif mode == "strm tv show dialog":
    episode_dialog(data, imdb_id, strm=True)
elif mode == "play":
    execute_video(name, imdb_id)
elif mode == "manual search":
    manual_search(data)
    xbmc.executebuiltin("Container.Refresh")
elif mode == "subscribe":
    subscribe(name, data)
    xbmc.executebuiltin("Container.Refresh")
elif mode == "unsubscribe":
    if name.find('[') >= 0:
        name = name.split('[')[0][:-1]
    unsubscribe(name, data)
    xbmc.executebuiltin("Container.Refresh")
elif mode == "get subscriptions":
    get_subscriptions()
elif mode == "toggle movie strm":
    name = clean_file_name(name)
    if exist_in_dir(name, MOVIES_PATH, isMovie=True):
        remove_strm_file(data, MOVIES_PATH)
        #clean_library()
    else:
        create_strm_file(name, data, imdb_id, "strm movie dialog", MOVIES_PATH)
        scan_library()
    xbmc.executebuiltin("Container.Refresh")
elif mode == "toggle tv show strms":
    data = clean_file_name(data.split('(')[0][:-1])
    if exist_in_dir(data, TV_SHOWS_PATH):
        remove_tv_show_strm_files(data, TV_SHOWS_PATH)
        #clean_library()
    else:
        create_tv_show_strm_files(data, imdb_id, "strm tv show dialog", TV_SHOWS_PATH)
        scan_library()
    xbmc.executebuiltin("Container.Refresh")

#Sort by ...
#TODO:
#max search saves
#torrent mode
#download and play

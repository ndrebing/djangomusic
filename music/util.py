import re
import requests
import json
from .models import Room, PlaylistItem
import numpy as np
import urllib.parse
import urllib.request
import urllib.error

playerStates = {"nicht gestartet": -1 , "beendet": 0, "wird wiedergegeben": 1, "pausiert": 2, "wird gepuffert": 3, "Video positioniert": 5}

def get_youtube_id(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)
    return youtube_regex_match

def get_youtube_content_from_id(id):
    payload = {'part':'snippet', 'id': id, 'key': 'AIzaSyDDBk8tAkod1VRRNyFZF09fgQyMpnSe5HI'}
    url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(payload)
    try:
        data = urllib.request.urlopen(url).read().decode("utf8")
    except urllib.error.HTTPError as e:

        return None, None
    except urllib.error.URLError as e:

        return None, None
    else:
        try:
            data = json.loads(data)
            #print((data['items'][0]['snippet']['title']))
            yt_title = data['items'][0]['snippet']['title']
            yt_thumbnail_url = data['items'][0]['snippet']['thumbnails']['default']['url']
            #assert(data['items'][0]['kind']=="youtube#video")
        except UnicodeEncodeError as e:

            return "UnicodeEncodeError", "UnicodeEncodeError"
        except:

            return None, None
    return yt_title, yt_thumbnail_url

def url_is_valid(url):
    return not re.search(r'[^a-zA-Z0-9]', url)

def pickNextSong(room):
    if not room.shuffle:
        if room.current_playlistItem is None:
            new_id = PlaylistItem.objects.filter(room=room).order_by('added')[0].id

        elif PlaylistItem.objects.filter(room=room).latest("id").id > room.current_playlistItem.id:
            valid_ids = [x['id'] for x in PlaylistItem.objects.filter(room=room).order_by('added').values('id')]

            new_id = valid_ids[valid_ids.index(room.current_playlistItem.id) + 1]
        else:
            new_id = PlaylistItem.objects.filter(room=room).order_by('added')[0].id

    else:
        while True:
            valid_ids = [x['id'] for x in PlaylistItem.objects.filter(room=room).values('id')]
            new_id = np.random.choice(valid_ids,1)[0]
            if new_id != room.current_playlistItem.id:
                break

    if new_id is not None:
        room.current_playlistItem = PlaylistItem.objects.filter(room=room).get(id=new_id)
    else:
        room.current_playlistItem = None

    room.vote_skip_list = ""
    room.save(update_fields=["current_playlistItem", "vote_skip_list"])

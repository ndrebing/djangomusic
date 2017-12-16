import re
import requests
import json
from .models import Room, PlaylistItem
import numpy as np

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
    r = requests.get("https://www.googleapis.com/youtube/v3/videos", params=payload)
    try:
        assert(r.status_code==200)
        data = json.loads(r.content)
        yt_title = data['items'][0]['snippet']['title']
        yt_thumbnail_url = data['items'][0]['snippet']['thumbnails']['default']['url']
        assert(data['items'][0]['kind']=="youtube#video")
    except:
        return None, None

    return yt_title, yt_thumbnail_url


def pickNextSong(room_url):
    room = Room.objects.get(url=room_url)
    current_playlistItem = room.current_playlistItem

    if not room.shuffle:
        print("Shuffle off")
        if current_playlistItem is None:
            new_id = PlaylistItem.objects.filter(room=room).order_by('added')[0].id

        elif PlaylistItem.objects.filter(room=room).latest("id").id > current_playlistItem.id:
            valid_ids = [x['id'] for x in PlaylistItem.objects.filter(room=room).order_by('added').values('id')]
            new_id = valid_ids[valid_ids.index(current_playlistItem.id) + 1]
        else:
            if not room.repeat:
                new_id = None
            else:
                new_id = PlaylistItem.objects.filter(room=room).order_by('added')[0].id
    else:
        while True:
            valid_ids = [x['id'] for x in PlaylistItem.objects.filter(room=room).values('id')]
            new_id = np.random.choice(valid_ids,1)[0]
            if new_id != current_playlistItem.id:
                break

    if new_id is not None:
        room.current_playlistItem = PlaylistItem.objects.filter(room=room).get(id=new_id)
    else:
        room.current_playlistItem = None

    room.vote_skip_list = ""
    room.save()

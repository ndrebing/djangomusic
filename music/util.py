import re
import requests
import json

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

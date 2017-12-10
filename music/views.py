from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import PlaylistItem, ConfigItem
from django.template import loader
from .forms import AddItemForm
from django.utils import timezone
import re
from django.http import JsonResponse
import logging
from django.db.utils import IntegrityError
import sqlite3
from urllib.parse import urlparse

# Get an instance of a logger
logger = logging.getLogger(__name__)

def change_config(request):
    if request.method == 'GET':
        shuffle_val = True if request.GET.get('shuffle', False) == "true" else False
        repeat_val = True if request.GET.get('repeat', False) == "true" else False

        d = ConfigItem(shuffle=shuffle_val, repeat=repeat_val)

        try:
            d.save()
            data = {
                'success': True
            }
            return JsonResponse(data)
        except:
           data = {
                'success': True
            }
        return JsonResponse(data)


def add_youtube_url(request):
    if request.method == 'GET':
        link = request.GET.get('link', None)
        logger.error('link: ' + link)

        # Parse given link
        try:
            youtube_id = urlparse(link).query[2:]
            if "&" in query:
                youtube_id = youtube_id.split("&")[0]
            logger.error('youtube_id: ' + youtube_id)
            #youtube_id = re.search('v=([\S]{6,16})', link).group(0)[2:]
        except:
            logger.error('Parsing of link failed2')
            data = {
                'is_added': False,
                'success': False,
                'youtube_id': 0
            }
            return JsonResponse(data)

        # Check if duplicate
        logger.error('PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists(): ' + str(PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists()))
        if (PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists()):
            data = {
                'is_added': False,
                'success': False,
                'youtube_id': youtube_id
            }
            return JsonResponse(data)

        # Add to database
        p = PlaylistItem(youtube_id=youtube_id, date_added=timezone.now(), date_played=timezone.now())

        try:
            p.save()
        except:
            data = {
                'is_added': False,
                'success': False,
                'youtube_id': youtube_id
            }
            return JsonResponse(data)

        # build data that is returned to javascript
        data = {
            'is_added': not PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists(),
            'success': True,
            'youtube_id': youtube_id
        }
        return JsonResponse(data)
    # should never POST data to this url
    else:
        return HttpResponse("You are doing it wrong")

def index(request):
    addItemForm = AddItemForm()
    playlist_items = PlaylistItem.objects.order_by('-date_added')
    template = loader.get_template('music/index.html')
    context = {
        'playlist_items': playlist_items,
        'addItemForm': addItemForm
    }
    return HttpResponse(template.render(context, request))

def detail(request, playlistitem_id):
    return HttpResponse("Title %s." % PlaylistItem.objects.get(id=playlistitem_id).youtube_id)

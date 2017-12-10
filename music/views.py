from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import PlaylistItem
from django.template import loader
from .forms import AddItemForm
from django.utils import timezone
import re
from django.http import JsonResponse
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def add_youtube_url(request):
    if request.method == 'GET':
        link = request.GET.get('link', None)

        # Parse given link
        try:
            youtube_id = re.search('v=([\S]{6,16})', link).group(0)[2:]
        except:
            data = {
                'is_added': False,
                'success': False,
                'youtube_id': 0
            }
            return JsonResponse(data)

        # Add to database

        p = PlaylistItem(youtube_id=youtube_id, date_added=timezone.now(), date_played=timezone.now())
        try:
            p.save()
        except:
            logger.error('Something went wrong!')
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

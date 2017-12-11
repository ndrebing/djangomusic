from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import PlaylistItem, ConfigItem, Profile
from django.template import loader
from .forms import LoginForm
from django.utils import timezone
import re
from django.http import JsonResponse
import logging
from django.db.utils import IntegrityError
import sqlite3
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Get an instance of a logger
logger = logging.getLogger(__name__)
youtube_api_key = "CO5ZIUFYwMY&key=AIzaSyBZOk4mXjHUwPQeuw8JiEic0HqD-Ji-A0k" ### private, please dont share

def youtube_url_validation(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)

    return youtube_regex_match

def change_config(request):
    if request.method == 'GET':
        shuffle_val = True if request.GET.get('shuffle', False) == "true" else False
        repeat_val = True if request.GET.get('repeat', False) == "true" else False
        ConfigItem.objects.all().delete()
        d = ConfigItem(shuffle=shuffle_val, repeat=repeat_val)
        success = False
        try:
            d.save()
            success = True
        except:
           pass

        data = {
            'success': success,
            'shuffle_val': shuffle_val,
            'repeat_val': repeat_val,
        }
        return JsonResponse(data)

def get_playlist(request):
    if request.user.is_authenticated:
        playlist = [entry.youtube_id for entry in PlaylistItem.objects.all()]
        logger.error(playlist)
        data = {
            'playlist': playlist,
            'playlist_length': len(playlist),
        }
        return JsonResponse(data)
    else:
        return HttpResponse("You are doing it wrong")

def add_youtube_url(request):
    if request.method == 'GET' and request.user.is_authenticated:
        link = request.GET.get('link', None)
        logger.error('link: ' + link)
        # Parse given link
        try:
            youtube_id = youtube_url_validation(link)
        except:
            logger.error('Parsing of link failed')
            data = {
                'is_added': False,
                'success': False,
                'youtube_id': 0
            }
            return JsonResponse(data)

        # Check if duplicate
        logger.error('PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists(): ' + str(PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists()))
        if (PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists()) or youtube_id == None:
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
    if request.user.is_authenticated:
        return HttpResponseRedirect("/play_music")
    else:
        loginForm = LoginForm()
        signupForm = LoginForm()
        template = loader.get_template('music/login.html')
        context = {
            'LoginForm': loginForm,
            'SignupForm': signupForm
        }
        return HttpResponse(template.render(context, request))

def play_music(request):
    if request.user.is_authenticated:
        playlist_items = PlaylistItem.objects.order_by('-date_added')
        template = loader.get_template('music/play_music.html')
        context = {
            'playlist_items': playlist_items,
            'username': request.user.username,
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(".")

def signup_action(request):
    username = request.POST.get('username', "")
    password = request.POST.get('password', "")
    data = {
       'success': False,
    }

    if request.user.is_authenticated or username == "" or password == "" :
        return HttpResponse("user or password empty or authenticated")
    try:
        new_user = User.objects.create_user(username, '', password)
    except:
        return HttpResponse("Username schon vergeben :(")
    try:
        login(request, new_user)
        return HttpResponseRedirect("/play_music")
    except:
        return HttpResponse("login failed")

def logout_action(request):
    logout(request)
    return HttpResponseRedirect(".")

def login_action(request):
    username = request.POST.get('username', "")
    password = request.POST.get('password', "")
    user = authenticate(request, username=username, password=password)
    logger.error(user, password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect("/play_music")
    else:
        return HttpResponse("Login failed :(")

def detail(request, playlistitem_id):
    if request.user.is_authenticated:
        return HttpResponse("Title %s." % PlaylistItem.objects.get(id=playlistitem_id).youtube_id)
    else:
        return HttpResponseRedirect(".")

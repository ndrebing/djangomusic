from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import PlaylistItem, Room, Profile
from django.template import loader
from django.utils import timezone
import re
from django.http import JsonResponse
import logging
from django.db.utils import IntegrityError
import sqlite3
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import random
import datetime
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from .models import genId
from music.forms import SignUpForm, LogInForm

###################################################################################################################################
logger = logging.getLogger(__name__)
youtube_api_key = "CO5ZIUFYwMY&key=AIzaSyBZOk4mXjHUwPQeuw8JiEic0HqD-Ji-A0k" ### private, please dont share
User = get_user_model()
###################################################################################################################################

def log_in(request):
    form = LogInForm()
    if request.method == 'POST':
        form = LogInForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)

                # Send user to last_room or generate a new one if new user
                profile = Profile.objects.get(user=user)
                if profile.last_room is not None:
                    return HttpResponseRedirect(profile.last_room.url)
                else:
                    return HttpResponseRedirect(str(genId()))
            return HttpResponse("Invalid username or password")

        else:
            print(form.errors)
    return render(request, 'music/log_in.html', {'form': form})

@login_required(login_url='log_in')
def log_out(request):
    logout(request)
    return HttpResponseRedirect("log_in")

def sign_up(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(username=data['username']).exists():
                return HttpResponse("Username exists")

            if data['password'] != data['password2']:
                return HttpResponse("Passwords are not the same")

            # TODO only allow long passwords?

            if User.objects.filter(email=data['email']).exists():
                return HttpResponse("Your email is already in use")

            user = User.objects.create_user(data['username'], data['email'] , data['password'])
            return HttpResponseRedirect("log_in")
        else:
            return HttpResponse(str(form.errors))

    return render(request, 'music/sign_up.html', {'form': form})

@login_required(login_url='log_in')
def user_list(request):
    users = User.objects.select_related('logged_in_user')
    for user in users:
        user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
    return render(request, 'music/user_list.html', {'users': users, 'username': request.user.username})

@login_required(login_url='log_in')
def room(request, url):
    room, created = Room.objects.get_or_create(url=url)
    playlistItems = list(PlaylistItem.objects.filter(room=room).order_by('added'))
    profile = Profile.objects.get(user=request.user)
    profile.last_room = room
    profile.save()

    return render(request, "music/room.html", {
        'url': url,
        'playlistItems': playlistItems,
        'user': request.user,
        'profile': profile,
        'room': room,
    })

#def create_database_integrity():
#    logger.debug("create_database_integrity")
#
#    # Playlist has at least one entry
#    playlistItems = list(PlaylistItem.objects.all())
#    if len(playlistItems) <= 0:
#        p = PlaylistItem(youtube_id="g9Ttm46ASk8", date_added=timezone.now(), date_played=timezone.now())
#        p.save()
#
#    # Make sure exatcly one config item exists
#    configItems = list(ConfigItem.objects.all())
#    if len(configItems) > 1:
#        c_temp = configItems[0]
#        ConfigItem.objects.all().delete()
#        c_temp.save()
#    elif len(configItems) <= 0:
#        c_temp = ConfigItem(shuffle=False, repeat=False, current_youtube_id=playlistItems[0])
#        c_temp.save()


# TODO change to websocket
#@login_required(login_url='log_in')
#def change_config(request):
#    if request.method == 'GET':
#        # Read Database (in casecreate_database_integrity() restored default )
#        shuffle_db = ConfigItem.objects.latest('id').shuffle
#        repeat_db = ConfigItem.objects.latest('id').repeat
#
#        shuffle = True if request.GET.get('shuffle', False) == "true" else False
#        repeat = True if request.GET.get('repeat', False) == "true" else False
#
#        # Update Database
#        try:
#            configItem = ConfigItem.objects.latest('id')
#            configItem.shuffle = shuffle
#            configItem.repeat = repeat
#            configItem.save()
#        except:
#            create_database_integrity()
#
#        if (shuffle != shuffle_db):
#            add_interface_log(request, "Changed Shuffle")
#
#        data = {
#            'shuffle_val': shuffle_db,
#            'repeat_val': repeat_db,
#        }
#        return JsonResponse(data)

# TODO change to websocket
#@login_required(login_url='log_in')
#def get_interface(request):
#    if request.user.is_authenticated:
#        playlist = [entry.youtube_id for entry in PlaylistItem.objects.all()]
#        interface_log_text = ""
#        for entry in interface_log[-20:]:
#            interface_log_text += entry +"\n"
#
#        try:
#            configItem  = ConfigItem.objects.all()[0]
#        except:
#            create_database_integrity()
#
#        data = {
#            'playlist': playlist,
#            'playlist_length': len(playlist),
#            'shuffle': configItem.shuffle,
#            'repeat': configItem.repeat,
#            'is_playing': configItem.is_playing,
#            'youtube_id': configItem.current_youtube_id.youtube_id,
#            'interface_log': interface_log_text,
#        }
#        return JsonResponse(data)
#    else:
#        return HttpResponse("You are doing it wrong")

# TODO change to websocket
#    -1 (nicht gestartet)
#    0 (beendet)
#    1 (wird wiedergegeben)
#    2 (pausiert)
#    3 (wird gepuffert)
#    5 (Video positioniert)
#@login_required(login_url='log_in')
#def notify_server(request):
#    if request.method == 'GET' and request.user.is_authenticated:
#        value = request.GET.get('status', None)
#
#        print("NOTIFICATON", value)
#        if value == None:
#            return HttpResponse("notification error: no status provided")
#        elif value == '-1':
#            new_id = random.sample(range(PlaylistItem.objects.latest("id").id),1)
#            configItem = ConfigItem.objects.latest('id')
#            configItem.current_youtube_id = PlaylistItem.objects.get(id=new_id)
#            configItem.save()
#
#        elif value == '0':
#            pickNextSong()
#
#        elif value == '1':
#            add_interface_log(request, "Started playback")
#            try:
#                configItem = ConfigItem.objects.latest('id')
#                configItem.is_playing = True
#                configItem.save()
#            except:
#                create_database_integrity()
#
#        elif value == '2':
#            add_interface_log(request, "Paused playback")
#            try:
#                configItem = ConfigItem.objects.latest('id')
#                configItem.is_playing = False
#                configItem.save()
#            except:
#                create_database_integrity()
#        return HttpResponse("notification: working as intended")

# TODO change to websocket
#@login_required(login_url='log_in')
#def add_youtube_url(request):
#    if request.method == 'GET' and request.user.is_authenticated:
#        link = request.GET.get('link', None)
#        logger.error('link: ' + link)
#        # Parse given link
#        try:
#            youtube_id = youtube_url_validation(link)
#        except:
#            logger.error('Parsing of link failed')
#            data = {
#                'is_added': False,
#                'success': False,
#                'youtube_id': 0
#            }
#            return JsonResponse(data)
#
#        # Check if duplicate
#        logger.error('PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists(): ' + str(PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists()))
#        if (PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists()) or youtube_id == None:
#            data = {
#                'is_added': False,
#                'success': False,
#                'youtube_id': youtube_id
#            }
#            return JsonResponse(data)
#
#        # Add to database
#        p = PlaylistItem(youtube_id=youtube_id, date_added=timezone.now(), date_played=timezone.now())
#
#        try:
#            p.save()
#        except:
#            data = {
#                'is_added': False,
#                'success': False,
#                'youtube_id': youtube_id
#            }
#            return JsonResponse(data)
#
#        add_interface_log(request, "Added " + link)
#
#        # build data that is returned to javascript
#        data = {
#            'is_added': not PlaylistItem.objects.filter(youtube_id__iexact=youtube_id).exists(),
#            'success': True,
#            'youtube_id': youtube_id
#        }
#        return JsonResponse(data)
#    # should never POST data to this url
#    else:
#        return HttpResponse("You are doing it wrong")

#def index(request):
#    if request.user.is_authenticated:
#        return HttpResponseRedirect("/play_music")
#    else:
#        loginForm = LoginForm()
#        signupForm = LoginForm()
#        template = loader.get_template('music/login.html')
#        context = {
#            'LoginForm': loginForm,
#            'SignupForm': signupForm
#        }
#        return HttpResponse(template.render(context, request))

#def play_music(request):
#    if request.user.is_authenticated:
#        playlist_items = PlaylistItem.objects.order_by('-date_added')
#        template = loader.get_template('music/play_music.html')
#        context = {
#            'playlist_items': playlist_items,
#            'username': request.user.username,
#        }
#        return HttpResponse(template.render(context, request))
#    else:
#        return HttpResponseRedirect(".")

#def vote_skip_action(request):
#    data = {
#        'is_added': False
#    }
#    if request.user.is_authenticated:
#
#        configItem = ConfigItem.objects.latest('id')
#        voted_ids = configItem.vote_skip_list
#
#        split_ids = voted_ids.split(';')
#        cnt = len(split_ids)-1
#        if not voted_ids:
#            voted_ids += (str(request.user.id) + ';')
#            cnt += 1
#            data = {
#                'is_added': True
#            }
#        else:
#            if any(str(request.user.id) in s for s in split_ids):
#                return JsonResponse(data)
#            else:
#                voted_ids += (str(request.user.id) + ';')
#                cnt +=1
#                data = {
#                    'is_added': True
#                }
#
#        configItem.vote_skip_list = voted_ids
#        configItem.save()
#        add_interface_log(request, "Voted to skip")
#        print("COUNT FOR VOTE NOW: " + str(cnt))
#
#        if cnt >= 2:
#            pickNextSong()
#        return JsonResponse(data)
#
#    else:
#        return JsonResponse(data)


#def pickNextSong():
#    # do what you want cause a pirate is freeeee
#    #TODO: handling of cases, doing something useful with it
#    configItem = ConfigItem.objects.latest('id')
#    shuffle = configItem.shuffle
#    repeat = configItem.repeat
#    current_playlistItem = configItem.current_youtube_id
#    if not shuffle:
#        if PlaylistItem.objects.latest("id").id > current_playlistItem.id:
#            valid_ids = [x['id'] for x in PlaylistItem.objects.order_by('date_added').values('id')]
#            new_id = valid_ids[valid_ids.index(current_playlistItem.id) + 1]
#        else:
#            new_id = PlaylistItem.objects.order_by('date_added')[0].id
#    else:
#        while True:
#            valid_ids = [x['id'] for x in PlaylistItem.objects.values('id')]
#            new_id = random.sample(valid_ids,1)[0]
#            print(new_id, current_playlistItem.id)
#            if new_id != current_playlistItem.id:
#                break
#    try:
#        configItem.current_youtube_id = PlaylistItem.objects.get(id=new_id)
#        configItem.vote_skip_list = ""
#        configItem.save()
#    except:
#        create_database_integrity()

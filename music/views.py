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
    playlistItems = PlaylistItem.objects.filter(room=room).order_by('added')
    profile = Profile.objects.get(user=request.user)
    profile.last_room = room
    profile.save()

    return render(request, "music/room.html", {
        'profile': profile,
        'room': room,
        'playlistItems': playlistItems,
    })

import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from music.util import get_youtube_content_from_id, get_youtube_id, pickNextSong
from .models import PlaylistItem, Room, Profile
from django.core import serializers
from django.contrib.auth.models import User
import logging
from music.util import playerStates, url_is_valid
import math

logger = logging.getLogger(__name__)

def get_room_url(message):
    # Different when online/localhost
    if "ws" in message.content['path']:
        return message.content['path'][6:]
    else:
        return message.content['path'][2:]

@channel_session_user_from_http
def ws_connect(message):
    try:
        # Parse URL from connecting path
        room_url = get_room_url(message)
    except:
        logger.error("message.content['path']:" +message.content['path'])
        return
    # if URL is invalid, dont return accept, room.html will return error to user
    if not url_is_valid(room_url):
        return

    # Send accept (Triggers connect on client side)
    message.reply_channel.send({"accept": True})

    # Set login in db to keep online users up to date
    profile = Profile.objects.get(user=message.user)
    profile.is_logged_in = True
    profile.save()

    # Add client to room group
    Group(room_url).add(message.reply_channel)

@channel_session_user
def ws_disconnect(message):
    # Analog to connect
    room_url = get_room_url(message)
    Group(room_url).discard(message.reply_channel)
    profile = Profile.objects.get(user=message.user)
    profile.is_logged_in = False
    profile.save()

def group_message(room_url, data):
    """
    Sends data to room
    """
    Group(room_url).send({
        'text': json.dumps(data)
    })

def return_message(message, data):
    message.reply_channel.send({
        'text': json.dumps(data)
    })

@channel_session_user
def ws_receive(message):
    data = json.loads(message['text'])

    user = message.user
    user_profile = Profile.objects.get(user=user)
    room_url = get_room_url(message)
    if not url_is_valid(room_url):
        return
    room = Room.objects.get(url=room_url)

    # Checking if valid
    # TODO necessary?
    try:
        assert(user_profile.last_room == room)
    except:
        return

    if data['message_type'] == "submit_url":
        possible_yt_id = data['message_content']
        yt_title, yt_thumbnail_url = get_youtube_content_from_id(possible_yt_id)
        if yt_title is not None:
            try:
                item = PlaylistItem.objects.get(youtube_id=possible_yt_id, room=user_profile.last_room)
            except PlaylistItem.DoesNotExist:
                item = None

            if item:
                return_message(message, {
                    'message_type': 'alert',
                    'message_content': yt_title + " has already been added by " + item.user_added.username,
                })
                pass
            else:
                item = PlaylistItem.objects.create(youtube_id=possible_yt_id, title=yt_title, thumbnail_link=yt_thumbnail_url, user_added=user, room=user_profile.last_room)
                group_message(room.url, {
                    'message_type': 'append_to_playlist',
                    'message_content': [item.title, item.thumbnail_link, user.username, item.youtube_id, len(PlaylistItem.objects.filter(room=room).all())],
                })
                if len(PlaylistItem.objects.filter(room=user_profile.last_room)) == 1:
                    room.current_playlistItem = item
                    room.is_playing = True
                    room.save(update_fields=["current_playlistItem", "is_playing"])

        else:
            return_message(message, {
                'message_type': 'alert',
                'message_content': "Invalid link " + str(possible_yt_id),
            })

    elif data['message_type'] == "voteskip":
        if(user_profile.last_room == room):
            if str(user.id) not in room.vote_skip_list.split(';'):
                room.vote_skip_list += (str(user.id) + ";")
                room.save(update_fields=["vote_skip_list"])
                votes_given = len(room.vote_skip_list.split(";")) - 1
                votes_needed = math.ceil(len(Profile.objects.filter(last_room=room, is_logged_in=True)) * room.vote_skip_rate)

                print("BBBB room.vote_skip_list", room.vote_skip_list, "given",votes_given, "votes_needed", votes_needed, "online", len(Profile.objects.filter(last_room=room, is_logged_in=True)), "room.vote_skip_list.split()", room.vote_skip_list.split(";"))

                if(votes_given >= votes_needed):
                    pickNextSong(room)




    elif data['message_type'] == "ready":
        if room.current_playlistItem is not None:

            if room.is_playing:
                message_type = "play"
            else:
                message_type = "pause"

            return_message(message, {
                'message_type': message_type,
                'message_content': None,
            })

    elif data['message_type'] == "toggle":
        button_type = data['message_content']
        button_text = button_type + "_button"

        if button_type == "shuffle":
            room.shuffle = not room.shuffle
        elif button_type == "repeat":
            room.repeat = not room.repeat
        room.save(update_fields=[button_type])

    elif data['message_type'] == "player_state_change":
        player_state = data['message_content']
        update_fields = []
        if player_state == playerStates["beendet"]:
            pickNextSong(room)
            room.is_playing = True
            update_fields = ["is_playing", "current_playlistItem"]
        elif player_state == playerStates["wird wiedergegeben"]:
            room.is_playing = True
            update_fields = ["is_playing"]
        elif player_state == playerStates["pausiert"]:
            room.is_playing = False
            update_fields = ["is_playing"]
        else:
            return
        room.save(update_fields=update_fields)

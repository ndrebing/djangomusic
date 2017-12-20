import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from music.util import get_youtube_content_from_id, get_youtube_id, pickNextSong
from .models import PlaylistItem, Room, Profile
from django.core import serializers
from django.contrib.auth.models import User
import logging
from music.util import playerStates
import math

logger = logging.getLogger(__name__)

def get_room_url(message):
    # Different when online/localhost
    if "ws" in message.content['path']:
        return message.content['path'][4:]
    else:
        return message.content['path'][1:]

@channel_session_user_from_http
def ws_connect(message):
    try:
        # Parse URL from connecting path
        room_url = get_room_url(message)
        assert(len(room_url) == 8)
    except:
        logger.error("message.content['path']:" +message.content['path'])
        return

    # Send accept (Triggers connect on client side)
    message.reply_channel.send({"accept": True})

    # Set login in db to keep online users up to date
    profile = Profile.objects.get(user=message.user)
    profile.is_logged_in = True
    profile.save()

    # Add client to room group
    Group(room_url).add(message.reply_channel)

    # Send update to room group to update user list
    send_room_update(room_url)

@channel_session_user
def ws_disconnect(message):
    # Analog to connect
    room_url = get_room_url(message)
    Group(room_url).discard(message.reply_channel)
    profile = Profile.objects.get(user=message.user)
    profile.is_logged_in = False
    profile.save()
    send_room_update(room_url)

def send_room_update(room_url):
    """
    Sends profile list of all users of room to room
    """
    room = Room.objects.get(url=room_url)
    all_usernames = [p.user.username for p in Profile.objects.filter(last_room=room, is_logged_in=True)]
    group_message(room_url, {
        'message_type': 'username_list_update',
        'message_content': all_usernames,
    })

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

    submitting_user = message.user
    user_profile = Profile.objects.get(user=submitting_user)
    room_url = get_room_url(message)
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
                item = PlaylistItem.objects.create(youtube_id=possible_yt_id, title=yt_title, thumbnail_link=yt_thumbnail_url, user_added=submitting_user, room=user_profile.last_room)
                group_message(room.url, {
                    'message_type': 'append_to_playlist',
                    'message_content': [item.title, item.thumbnail_link, submitting_user.username, item.youtube_id, len(PlaylistItem.objects.filter(room=room).all())],
                })
                if len(PlaylistItem.objects.filter(room=user_profile.last_room)) == 1:
                    room.current_playlistItem = item
                    room.is_playing = True
                    room.save(update_fields=["is_playing"])

        else:
            return_message(message, {
                'message_type': 'alert',
                'message_content': "Invalid link " + str(possible_yt_id),
            })

    elif data['message_type'] == "voteskip":
        # get logged in users
        user_id = submitting_user.id
        vote_list = room.vote_skip_list
        skip_val = False
        # is user permitted to send to this room?
        if(user_profile.last_room == room):
            vote_list_parse = vote_list.split(';')
            vote_cnt = len(vote_list_parse) - 1
            print("lol")
            if str(user_id) not in vote_list_parse:
                print("lol2")
                print("userid: " + str(user_id) )
                vote_list += (str(user_id) + ";")
                vote_cnt += 1

                # update skiplist
                room.vote_skip_list = vote_list
                room.save()

            #### skip condition, TODO: has ddos potential, save number of users in database
            all_usernames = [p.user.username for p in Profile.objects.filter(last_room=room, is_logged_in=True)]
            cnt = math.ceil(len(all_usernames) / 2)
            if(vote_cnt >= cnt):
                skip_val = True
                pickNextSong(room)

                date_str = room.current_playlistItem.added.strftime("%S:%M:%H %d.%m.%Y")
                group_message(room.url, {
                'message_type': 'voteskip',
                'message_content': [[room.current_playlistItem.title, room.current_playlistItem.user_added.username, date_str], room.current_playlistItem.youtube_id],
                'skip': skip_val
                })
                return
            #update counter
            cnt_perc = math.ceil((vote_cnt / cnt)*100)
            group_message(room.url, {
            'message_type': "voteskip",
            'votes_needed' : cnt,
            'votes' : vote_cnt,
            'votes_percent' : cnt_perc,
            'skip': skip_val
            })


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
              
        if player_state == playerStates["beendet"]:
            pickNextSong(room)
            room.is_playing = True
        elif player_state == playerStates["wird wiedergegeben"]:
            room.is_playing = True
        elif player_state == playerStates["pausiert"]:
            room.is_playing = False
        else:
            return
            
        room.save(update_fields=["is_playing"])
        

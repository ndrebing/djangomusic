import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from music.util import get_youtube_content_from_id, get_youtube_id, pickNextSong
from .models import PlaylistItem, Room, Profile
from django.core import serializers
from django.contrib.auth.models import User

@channel_session_user_from_http
def ws_connect(message):
    #message.reply_channel.send({"accept": True})
    room_url = message.content['path'].split("/")[2]
    Group(room_url).add(message.reply_channel)
    send_room_update(room_url)


@channel_session_user
def ws_disconnect(message):
    room_url = message.content['path'].split("/")[2]
    Group(room_url).discard(message.reply_channel)
    send_room_update(room_url)

def send_room_update(room_url):
    """
    Sends profile list of all users of room to room
    """
    room = Room.objects.get(url=room_url)
    all_usernames = [p.user.username for p in Profile.objects.filter(last_room=room)]
    send_message(room_url, {
        'message_type': 'username_list_update',
        'message_content': all_usernames,
        'message_origin': "server",
    })

def send_message(room_id, data):
    """
    Sends data to room
    """
    Group(room_id).send({
        'text': json.dumps(data)
    })

@channel_session_user
def ws_receive(message):
    data = json.loads(message['text'])

    # Checking if valid
    # TODO necessary?
    submitting_user = message.user
    user_profile = Profile.objects.get(user=submitting_user)
    room_url = data['message_origin']


    if data['message_type'] == "submit_url":
        possible_yt_id = data['message_content']
        yt_title, yt_thumbnail_url = get_youtube_content_from_id(possible_yt_id)
        if yt_title is not None:
            try:
                item = PlaylistItem.objects.get(youtube_id=possible_yt_id, room=user_profile.last_room)
            except PlaylistItem.DoesNotExist:
                item = None

            if item:
                send_message(room_url, {
                    'message_type': 'alert',
                    'message_content': yt_title + " has already been added by " + item.user_added.username,
                    'message_origin': "server",
                })
                print("already added")
                pass
            else:
                item = PlaylistItem.objects.create(youtube_id=possible_yt_id, title=yt_title, thumbnail_link=yt_thumbnail_url, user_added=submitting_user, room=user_profile.last_room)
                # TODO alert users in room to add new playlist item
                send_message(room_url, {
                    'message_type': 'append_to_playlist',
                    'message_content': [item.title, item.thumbnail_link, submitting_user.username, item.youtube_id],
                    'message_origin': "server",
                })
        else:
            send_message(room_url, {
                'message_type': 'alert',
                'message_content': "Invalid link " + str(possible_yt_id),
                'message_origin': "server",
            })

    elif data['message_type'] == "finished_loading":
        room = Room.objects.get(url=room_url)
        if room.is_playing:
            message_type = "play"
        else:
            message_type = "pause"

        send_message(room_url, {
            'message_type': message_type,
            'message_content': "",
            'message_origin': "server",
        })

    elif data['message_type'] == "toggle_shuffle":
        room = Room.objects.get(url=room_url)
        room.shuffle = not room.shuffle
        room.save()

        send_message(room_url, {
            'message_type': "change_shuffle_button",
            'message_content': room.shuffle,
            'message_origin': "server",
        })
    elif data['message_type'] == "toggle_repeat":
        room = Room.objects.get(url=room_url)
        room.repeat = not room.repeat
        room.save()

        send_message(room_url, {
            'message_type': "change_repeat_button",
            'message_content': room.repeat,
            'message_origin': "server",
        })
    elif data['message_type'] == "player_state_change":
        player_state = data['message_content']
        message_type = "pause"
        message_content = ""

        if player_state == 1:
            message_type = "play"
        elif player_state == 2:
            message_type = "pause"
        elif player_state == 3:
            message_type = "pause"

        # video finished
        elif player_state == 0:
            pickNextSong(room_url)
            message_type = "load"
            message_content = Room.objects.get(url=room_url).current_playlistItem.youtube_id

        send_message(room_url, {
            'message_type': message_type,
            'message_content': message_content,
            'message_origin': "server",
        })

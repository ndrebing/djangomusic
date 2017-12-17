import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from music.util import get_youtube_content_from_id, get_youtube_id, pickNextSong
from .models import PlaylistItem, Room, Profile
from django.core import serializers
from django.contrib.auth.models import User


@channel_session_user_from_http
def ws_connect(message):

    # Parse URL from connecting path
    room_url = message.content['path'].split("/")[2]

    # Send accept (Triggers connect on client side)
    message.reply_channel.send({"accept": True})

    # Add client to room group
    Group(room_url).add(message.reply_channel)

    # Send update to room group to update user list
    send_room_update(room_url)

@channel_session_user
def ws_disconnect(message):
    # Analog to connect
    room_url = message.content['path'].split("/")[2]
    Group(room_url).discard(message.reply_channel)
    send_room_update(room_url)

def send_room_update(room_url):
    """
    Sends profile list of all users of room to room
    """
    room = Room.objects.get(url=room_url)
    all_usernames = [p.user.username for p in Profile.objects.filter(last_room=room, is_logged_in=True)]
    send_message(room_url, {
        'message_type': 'username_list_update',
        'message_content': all_usernames,
    })

def send_message(room_url, data):
    """
    Sends data to room
    """
    Group(room_url).send({
        'text': json.dumps(data)
    })

@channel_session_user
def ws_receive(message):
    data = json.loads(message['text'])

    submitting_user = message.user
    user_profile = Profile.objects.get(user=submitting_user)
    room_url = message.content['path'].split("/")[2]
    room = Room.objects.get(url=room_url)

    # Checking if valid
    # TODO necessary?
    assert(user_profile.last_room == room)

    if data['message_type'] == "submit_url":
        possible_yt_id = data['message_content']
        yt_title, yt_thumbnail_url = get_youtube_content_from_id(possible_yt_id)
        if yt_title is not None:
            try:
                item = PlaylistItem.objects.get(youtube_id=possible_yt_id, room=user_profile.last_room)
            except PlaylistItem.DoesNotExist:
                item = None

            if item:
                send_message(reply_id, {
                    'message_type': 'alert',
                    'message_content': yt_title + " has already been added by " + item.user_added.username,
                })
                print("already added")
                pass
            else:
                item = PlaylistItem.objects.create(youtube_id=possible_yt_id, title=yt_title, thumbnail_link=yt_thumbnail_url, user_added=submitting_user, room=user_profile.last_room)
                # TODO alert users in room to add new playlist item
                send_message(room.url, {
                    'message_type': 'append_to_playlist',
                    'message_content': [item.title, item.thumbnail_link, submitting_user.username, item.youtube_id, len(PlaylistItem.objects.all())],
                })
        else:
            send_message(room.url, {
                'message_type': 'alert',
                'message_content': "Invalid link " + str(possible_yt_id),
            })

    elif data['message_type'] == "ready":
        print("got ready")
        if room.is_playing:
            message_type = "play"
        else:
            message_type = "pause"

        send_message(room.url, {
            'message_type': message_type,
            'message_content': room.current_playlistItem.youtube_id,
        })

    elif data['message_type'] == "toggle_shuffle":
        room.shuffle = not room.shuffle
        room.save()

        send_message(room.url, {
            'message_type': "change_shuffle_button",
            'message_content': room.shuffle,
        })
    elif data['message_type'] == "toggle_repeat":
        room.repeat = not room.repeat
        room.save()

        send_message(room.url, {
            'message_type': "change_repeat_button",
            'message_content': room.repeat,
        })
    elif data['message_type'] == "player_state_change":
        player_state = data['message_content']
        message_content = room.current_playlistItem.youtube_id

        if player_state == 1:
            message_type = "play"
        elif player_state == 2:
            message_type = "pause"
        elif player_state == 3:
            message_type = "pause"
        elif player_state == 0:
            message_type = "play"
            pickNextSong(room.url)
        else:
            message_type = "unhandeld"

        send_message(room.url, {
            'message_type': message_type,
            'message_content': message_content,
        })

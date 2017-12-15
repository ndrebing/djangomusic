import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from music.util import get_youtube_content_from_id, get_youtube_id
from .models import PlaylistItem, Room, Profile
from django.core import serializers

@channel_session_user_from_http
def ws_connect(message):
    #Group('users').add(message.reply_channel)
    #Group('users').send({
    #    'text': json.dumps({
    #        'message_type': 'login_event',
    #        'username': message.user.username,
    #        'is_logged_in': True
    #    })
    #})
    message.reply_channel.send({"accept": True})
    Group(str(message.content['path'].split("/")[2])).add(message.reply_channel)

@channel_session_user
def ws_disconnect(message):
    #Group('users').send({
    #    'text': json.dumps({
    #        'message_type': 'login_event',
    #        'username': message.user.username,
    #        'is_logged_in': False
    #    })
    #})
    #Group('users').discard(message.reply_channel)
    Group(str(message.content['path'].split("/")[2])).discard(message.reply_channel)

def send_message(room_id, data):
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
    try:
        assert(Room.objects.get(url=room_url) == user_profile.last_room)
    except:
        print(Room.objects.get(url=room_url))
        print(user_profile.last_room)
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
                    'message_content': [item.title, item.thumbnail_link, submitting_user.username],
                    'message_origin': "server",
                })
        else:
            send_message(room_url, {
                'message_type': 'alert',
                'message_content': "Invalid link " + str(possible_yt_id),
                'message_origin': "server",
            })

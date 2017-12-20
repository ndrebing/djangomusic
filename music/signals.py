from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from music.models import Profile, Room
from music.consumers import group_message
from music.util import playerStates, pickNextSong
import math

def send_room_update(room):
    group_message(room.url, {
        'message_type': 'username_list_update',
        'message_content': [p.user.username for p in Profile.objects.filter(last_room=room, is_logged_in=True)],
    })

@receiver(user_logged_in)
def on_user_login(sender, **kwargs):
    profile = Profile.objects.get(user=kwargs.get('user'))
    profile.is_logged_in = True
    profile.save()
    last_room = profile.last_room
    if last_room is not None:
        send_room_update(last_room)

@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    profile = Profile.objects.get(user=kwargs.get('user'))
    profile.is_logged_in = False
    profile.save()
    send_room_update(profile.last_room)


@receiver(post_save, sender=Room)
def post_save_room(sender, *args, **kwargs):
    room = kwargs.get('instance')
    update_fields = kwargs.get('update_fields')

    if kwargs.get('update_fields') is not None:

        if "is_playing" in update_fields or "current_playlistItem" in update_fields:
            if room.is_playing:
                target_player_state = playerStates["wird wiedergegeben"]
            else:
                target_player_state = playerStates["pausiert"]

            if room.current_playlistItem is not None:
                date_str = room.current_playlistItem.added.strftime("%Y-%m-%d %H:%M:%S")
                message_content = [[room.current_playlistItem.title, room.current_playlistItem.user_added.username, date_str], room.current_playlistItem.youtube_id, target_player_state]
                group_message(room.url, {
                    'message_type': "player",
                    'message_content': message_content,
                })

        if "shuffle" in update_fields:
            if room.shuffle:
                 message_content = [["shuffle_button", "class", "btn btn-primary active"], ["repeat_button", "aria-pressed", "true"]]
            else:
                 message_content = [["shuffle_button", "class", "btn btn-secondary"], ["repeat_button", "aria-pressed", "false"]]
            group_message(room.url, {
            'message_type': "change",
            'message_content': message_content,
        })

        if "repeat" in update_fields:
            if room.repeat:
                 message_content = [["repeat_button", "class", "btn btn-primary active"], ["repeat_button", "aria-pressed", "true"]]
            else:
                 message_content = [["repeat_button", "class", "btn btn-secondary"], ["repeat_button", "aria-pressed", "false"]]
            group_message(room.url, {
            'message_type': "change",
            'message_content': message_content,
        })

        if "vote_skip_list" in update_fields:
            print("AAA room.vote_skip_list", room.vote_skip_list)
            votes_given = len(room.vote_skip_list.split(";")) - 1
            votes_needed = math.ceil(len(Profile.objects.filter(last_room=room, is_logged_in=True)) * room.vote_skip_rate)
            print("AAA votes_given", votes_given, "votes_needed", votes_needed)
            group_message(room.url, {
                'message_type': "voteskip",
                'message_content': [votes_given, votes_needed]
            })

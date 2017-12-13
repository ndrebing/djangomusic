from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
import uuid
from django.conf import settings

class Room(models.Model):
    url = models.UUIDField(default=uuid.uuid4, editable=False)

class PlaylistItem(models.Model):
    youtube_id = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=200, default="No title")
    thumbnail_link = models.CharField(max_length=200, default="")
    last_played = models.DateTimeField(auto_now_add=True, blank=True)
    user_added = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)
    room = models.ForeignKey("Room", on_delete=models.CASCADE)

    def __str__(self):
        return self.youtube_id

class ConfigItem(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    playlistItem = models.ForeignKey("PlaylistItem", on_delete=models.CASCADE)
    shuffle = models.BooleanField(default=False)
    repeat = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)
    vote_skip_list = models.TextField(default='')

class LoggedInUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='logged_in_user', on_delete=models.CASCADE, primary_key=True)

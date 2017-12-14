from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
import uuid
from django.conf import settings
import string
import numpy as np

seed = int(uuid.uuid4()) % 1000000
np.random.seed(seed)

def genId(length=8):
    base = list(string.ascii_letters+string.digits)
    while True:
        hash_value = ""
        for i in range(length):
            hash_value += np.random.choice(base)
        if not Room.objects.filter(url=hash_value).exists():
            break
    return hash_value

class Room(models.Model):
    url = models.CharField(max_length=8, default=genId, unique=True, primary_key=True)
    current_playlistItem = models.ForeignKey("PlaylistItem", related_name="current_playlistItem", on_delete=models.CASCADE, blank=True, null=True)
    shuffle = models.BooleanField(default=False)
    repeat = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)
    vote_skip_list = models.CharField(max_length=2000, default='')

class PlaylistItem(models.Model):
    youtube_id = models.CharField(max_length=20)
    title = models.CharField(max_length=200, default="No title")
    thumbnail_link = models.CharField(max_length=200, default="")
    last_played = models.DateTimeField(auto_now_add=True, blank=True)
    added = models.DateTimeField(auto_now_add=True, blank=True)
    user_added = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey("Room", related_name="playlist_item_room", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='logged_in_user', on_delete=models.CASCADE, primary_key=True)
    last_room = models.ForeignKey("Room", on_delete=models.CASCADE, blank=True, null=True)
    is_logged_in = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get(user=instance).save()

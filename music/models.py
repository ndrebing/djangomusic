from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

class PlaylistItem(models.Model):
    youtube_id = models.CharField(max_length=16, unique=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True)
    date_played = models.DateTimeField(auto_now_add=True, blank=True)
    play_count = models.IntegerField(default=0)

    def __str__(self):
        return self.youtube_id

    def was_played_recently(self):
        return self.last_played >= timezone.now() - datetime.timedelta(days=1)

class ConfigItem(models.Model):
    current_youtube_id = models.ForeignKey("PlaylistItem", on_delete=models.PROTECT)
    shuffle = models.BooleanField(default=False)
    repeat = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)
    vote_skip_list = models.TextField(default='')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    player_state = models.TextField(blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

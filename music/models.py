from django.db import models
from django.utils import timezone
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
    shuffle = models.BooleanField(default=False)
    repeat = models.BooleanField(default=False)

class PlayState(models.Model):
    playing_youtube_id = models.ForeignKey("PlaylistItem", on_delete=models.PROTECT)

    # 0: Stop, 1: Play
    play_state = models.IntegerField(default=0)

    # 0: False, 1: True
    shuffle = models.IntegerField(default=0)

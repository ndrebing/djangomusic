from django.contrib import admin
from .models import PlaylistItem, ConfigItem, Room

admin.site.register(PlaylistItem)
admin.site.register(ConfigItem)
admin.site.register(Room)

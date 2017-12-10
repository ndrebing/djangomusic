from django.contrib import admin
from .models import PlaylistItem, PlayState, ConfigItem

admin.site.register(PlaylistItem)
admin.site.register(PlayState)
admin.site.register(ConfigItem)

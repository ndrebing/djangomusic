from django.contrib import admin
from .models import PlaylistItem, ConfigItem, Profile

admin.site.register(PlaylistItem)
admin.site.register(ConfigItem)
admin.site.register(Profile)

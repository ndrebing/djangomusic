from django.contrib import admin
from .models import PlaylistItem, Profile, Room

admin.site.register(PlaylistItem)
admin.site.register(Room)
admin.site.register(Profile)

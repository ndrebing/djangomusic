from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('play_music', views.play_music, name='play_music'),
    path('<int:playlistitem_id>/', views.detail, name='detail'),
    path('ajax/add_youtube_url/', views.add_youtube_url, name='add_youtube_url'),
    path('ajax/change_config/', views.change_config, name='change_config'),
    path('ajax/get_playlist/', views.get_playlist, name='get_playlist'),
]

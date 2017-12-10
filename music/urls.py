from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:playlistitem_id>/', views.detail, name='detail'),
    path('ajax/add_youtube_url/', views.add_youtube_url, name='add_youtube_url'),
    path('ajax/change_config/', views.change_config, name='change_config')
]

from django.urls import path

from . import views

urlpatterns = [
    path('', views.log_in, name='index'),
    path('user_list', views.user_list, name='user_list'),
    path('log_in', views.log_in, name='log_in'),
    path('log_out', views.log_out, name='log_out'),
    path('sign_up', views.sign_up, name='sign_up'),
]

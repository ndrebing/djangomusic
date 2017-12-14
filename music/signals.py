from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from music.models import Profile


@receiver(user_logged_in)
def on_user_login(sender, **kwargs):
    profile = Profile.objects.filter(user=kwargs.get('user'))
    profile.is_logged_in = True
    profile.save()

@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    profile = Profile.objects.filter(user=kwargs.get('user'))
    profile.is_logged_in = False
    profile.save()

# Generated by Django 2.0 on 2017-12-08 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_remove_playlistitem_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlistitem',
            name='youtube_id',
            field=models.CharField(max_length=16, unique=True),
        ),
    ]
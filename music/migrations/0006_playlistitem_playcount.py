# Generated by Django 2.0 on 2017-12-20 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_auto_20171220_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlistitem',
            name='playcount',
            field=models.IntegerField(default=0),
        ),
    ]
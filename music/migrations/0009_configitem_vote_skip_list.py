# Generated by Django 2.0 on 2017-12-11 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0008_configitem_is_playing'),
    ]

    operations = [
        migrations.AddField(
            model_name='configitem',
            name='vote_skip_list',
            field=models.TextField(blank=True),
        ),
    ]

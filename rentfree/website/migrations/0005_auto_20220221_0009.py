# Generated by Django 3.2.12 on 2022-02-21 06:09

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20220209_0540'),
        ('website', '0004_alter_podcastcontentpage_episode_preview'),
    ]

    operations = [
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_count', models.SmallIntegerField(default=1)),
                ('last', models.DateField(default=datetime.datetime.now)),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.custommedia')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customuserprofile')),
            ],
        ),
        migrations.AddField(
            model_name='custommedia',
            name='downloads',
            field=models.ManyToManyField(related_name='media_download', through='website.Download', to='users.CustomUserProfile'),
        ),
    ]

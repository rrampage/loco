# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-02 13:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('locations', '0003_auto_20171107_2103'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('timestamp', models.DateTimeField()),
                ('accuracy', models.FloatField()),
                ('spoofed', models.BooleanField()),
                ('battery', models.IntegerField()),
                ('session', models.CharField(blank=True, max_length=32, null=True)),
                ('action_type', models.CharField(choices=[(b'on', b'on'), (b'off', b'off')], max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

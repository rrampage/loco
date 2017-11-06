# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-06 11:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0003_auto_20171007_2225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attendance',
            old_name='action',
            new_name='action_type',
        ),
        migrations.AddField(
            model_name='attendance',
            name='accuracy',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='battery',
            field=models.IntegerField(default=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='session',
            field=models.CharField(default='asdf', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='spoofed',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='checkin',
            name='accuracy',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='checkin',
            name='battery',
            field=models.IntegerField(default=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='checkin',
            name='session',
            field=models.CharField(default='asdf', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='checkin',
            name='spoofed',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='checkin',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

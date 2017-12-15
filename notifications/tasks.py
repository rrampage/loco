from __future__ import absolute_import, unicode_literals
import json

from celery import shared_task

from .gcm import send_gcm


@shared_task
def send_gcm_async(gcm_token, data):
    send_gcm(gcm_token, data)

@shared_task
def addnum(x,y):
    return x+y
from __future__ import absolute_import, unicode_literals
import json

from celery import shared_task

from .gcm import send_checkin_gcm, send_chat_gcm


@shared_task
def send_checkin_gcm_async(checkin_id):
    send_checkin_gcm(checkin_id)

@shared_task
def send_chat_gcm_async(gcm_token):
    send_chat_gcm(checkin_id)

@shared_task
def addnum(x,y):
    return x+y
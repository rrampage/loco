from django.db.models import F, Max
from django.conf import settings
from django.db import models

from loco.models import BaseLocationModel

class UserLocation(BaseLocationModel):
	pass

class LocationStatus(BaseLocationModel):
    ACTION_ON = 'on'
    ACTION_OFF = 'off'

    ACTION_CHOICES = (
        (ACTION_ON, 'on'),
        (ACTION_OFF, 'off'),
    )

    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)

class PhoneStatus(BaseLocationModel):
    ACTION_ON = 'on'
    ACTION_OFF = 'off'

    ACTION_CHOICES = (
        (ACTION_ON, 'on'),
        (ACTION_OFF, 'off'),
    )

    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
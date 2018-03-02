from django.db.models import F, Max
from django.conf import settings
from django.db import models

from loco.models import BaseLocationModel
from teams.models import Team

class UserLocation(BaseLocationModel):
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, null=True, blank=True)

class LocationStatus(BaseLocationModel):
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, null=True, blank=True)
    ACTION_ON = 'on'
    ACTION_OFF = 'off'

    ACTION_CHOICES = (
        (ACTION_ON, 'on'),
        (ACTION_OFF, 'off'),
    )

    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)

class PhoneStatus(BaseLocationModel):
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, null=True, blank=True)
    ACTION_ON = 'on'
    ACTION_OFF = 'off'

    ACTION_CHOICES = (
        (ACTION_ON, 'on'),
        (ACTION_OFF, 'off'),
    )

    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
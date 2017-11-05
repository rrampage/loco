from django.db import models
from django.conf import settings

from loco.models import BaseModel

from locations.models import UserLocation

class UserAttendance(BaseModel):
    EVENT_SIGNIN = 'signin'
    EVENT_SIGNOUT= 'signout'

    EVENT_CHOICES = (
        (EVENT_SIGNIN, 'signin'),
        (EVENT_SIGNOUT, 'signout'),
    )

    timestamp = models.DateTimeField()
    session = models.CharField(max_length=32)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="events")
    event_type = models.CharField(max_length=10, choices=EVENT_CHOICES)
    location = models.ForeignKey(UserLocation, blank=True, null=True)
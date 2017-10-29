from django.conf import settings
from django.db import models

from loco.models import BaseModel

class UserLocation(BaseModel):
	latitude = models.FloatField()
	longitude = models.FloatField()
	timestamp = models.DateTimeField()
	accuracy = models.FloatField()
	spoofed = models.BooleanField()
	battery = models.IntegerField()
	session = models.CharField(max_length=32)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="locations")
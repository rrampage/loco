from django.db.models import F, Max
from django.conf import settings
from django.db import models

from loco.models import BaseLocationModel

class UserLocation(BaseLocationModel):
	pass

def get_users_location(users):
	return UserLocation.objects.filter(user__in=users).annotate(
		max_date=Max('user__userlocation__timestamp')).filter(timestamp=F('max_date'))

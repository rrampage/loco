from django.db import models
from django.conf import settings

class BaseModel(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

class BaseLocationModel(BaseModel):
	latitude = models.FloatField()
	longitude = models.FloatField()
	timestamp = models.DateTimeField()
	accuracy = models.FloatField()
	spoofed = models.BooleanField()
	battery = models.IntegerField()
	session = models.CharField(max_length=32)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

	class Meta:
		abstract = True
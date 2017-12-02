import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from loco.models import BaseModel
from loco.services import cache

from .usermanager import UserManager, UserOtpManager

from teams import constants as teams_constants

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=80)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True,)
    gcm_token = models.CharField(max_length=500, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    is_staff = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        new = False
        if self.pk is None:
            new = True

        super(User, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.get_full_name() + ": " + str(self.phone)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        "Returns the short name for the user."
        return self.name

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save()

    def update_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.save()

    def update_online(self, status):
        self.is_online = status
        self.save()
        if status:
            cache.set_user_status(self.id, cache.USER_STATUS_SIGNEDIN)
        else:
            cache.set_user_status(self.id, cache.USER_STATUS_SIGNEDOUT)

    def get_current_status(self):
        status = cache.get_user_status(self.id)
        return status

    def get_memberships(self):
        return self.teammembership_set.exclude(status=teams_constants.STATUS_ACCEPTED)

class UserOtp(BaseModel):
    otp = models.CharField(max_length=6)
    user = models.OneToOneField(User)

    objects = UserOtpManager()

class UserDump(BaseModel):
    data = models.TextField(blank=True, null=True)
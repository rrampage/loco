import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models

from loco.models import BaseModel

from . import constants


class Team(BaseModel):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='creator', on_delete=models.DO_NOTHING)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='TeamMembership',
        through_fields=('team', 'user'),
    )

    def save(self, *args, **kwargs):
        newly_created = True
        if self.id:
            newly_created = False

        super(Team, self).save(*args, **kwargs)

        if newly_created:
            TeamMembership.objects.create(
                team = self,
                user = self.created_by,
                created_by = self.created_by,
                role = TeamMembership.ROLE_ADMIN,
                status = constants.STATUS_ACCEPTED
            )

    def is_member(self, user):
        return TeamMembership.objects.filter(team=self, user=user).exists()

    def is_admin(self, user):
        return TeamMembership.objects.filter(
            team=self, user=user, role=TeamMembership.ROLE_ADMIN).exists()

    def add_member(self, user, created_by):
        if not self.is_member(user):
            return TeamMembership.objects.create(
                team = self,
                user = user,
                created_by = created_by,
                role = TeamMembership.ROLE_MEMBER,
                status = constants.STATUS_INVITED
            )

    def get_chat_members(self, user):
        try:
            membership = TeamMembership.objects.get(user=user, team=self)
            if membership.role == TeamMembership.ROLE_ADMIN:
                return TeamMembership.objects.filter(team=self).exclude(user=user)
            elif membership.role == TeamMembership.ROLE_MEMBER:
                return TeamMembership.objects.filter(team=self, role=TeamMembership.ROLE_ADMIN)
        except ObjectDoesNotExist:
            pass

        return []


class TeamMembership(BaseModel):
    ROLE_MEMBER = 'member'
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'

    ROLE_CHOICES = (
        (ROLE_MEMBER, 'member'),
        (ROLE_ADMIN, 'admin'),
        (ROLE_MANAGER, 'manager'),
    )

    STATUS_CHOICES = (
        (constants.STATUS_INVITED, 'invited'),
        (constants.STATUS_ACCEPTED, 'accepted'),
        (constants.STATUS_REJECTED, 'rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="invites", on_delete=models.DO_NOTHING)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=constants.STATUS_INVITED)

    def accept(self):
        self.status = constants.STATUS_ACCEPTED
        self.save()

    def reject(self):
        self.status = constants.STATUS_REJECTED
        self.save()

class Checkin(BaseModel):
    latitude = models.FloatField()
    longitude = models.FloatField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    description = models.TextField()

def checkin_media_path(instance, filename):
    return 'teams/{0}/users/{1}/checkins/{2}/{3}'.format(
        instance.team.id, instance.user.id, instance.unique_id, filename)

class CheckinMedia(BaseModel):
    checkin = models.ForeignKey(
        Checkin, null=True, on_delete=models.DO_NOTHING, related_name="media")
    media = models.FileField(upload_to=checkin_media_path)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Attendance(BaseModel):
    ACTION_SIGNIN = 'signin'
    ACTION_SIGNOUT = 'signout'

    ACTION_CHOICES = (
        (ACTION_SIGNIN, 'signin'),
        (ACTION_SIGNOUT, 'signout'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    latitude = models.FloatField()
    longitude = models.FloatField()

def user_media_path(instance, filename):
    return 'teams/{0}/users/{1}/{2}/{3}'.format(
        instance.team.id, instance.user.id, instance.unique_id, filename)

class UserMedia(BaseModel):
    media = models.FileField(upload_to=user_media_path)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
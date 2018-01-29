import uuid, random

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models

from loco.models import BaseModel, BaseLocationModel

from . import constants


_CODE_BASE = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

def get_team_code():
    code = ''
    secure_random = random.SystemRandom()
    for i in range(6):
        code += secure_random.choice(_CODE_BASE)

    return code

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
    code = models.CharField(max_length=10, default=get_team_code, unique=True)

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

    def join_team(self, user, code):
        if self.code != code:
            return False

        membership = TeamMembership.objects.filter(team=self, user=user)
        if not membership.exists():
            membership = TeamMembership.objects.create(
                team = self,
                user = user,
                created_by = user,
                role = TeamMembership.ROLE_MEMBER,
                status = constants.STATUS_INVITED
            )
        else:
            membership = membership[0]

        return membership

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

    def get_chat_targets(self, user):
        try:
            membership = TeamMembership.objects.get(user=user, team=self)
            if membership.role == TeamMembership.ROLE_ADMIN:
                return TeamMembership.objects.filter(team=self, role=TeamMembership.ROLE_ADMIN).exclude(user=user)
            elif membership.role == TeamMembership.ROLE_MEMBER:
                return TeamMembership.objects.filter(team=self, role=TeamMembership.ROLE_ADMIN)
        except ObjectDoesNotExist:
            pass

        return []

    def _sort_events(self, events):
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events

    def get_visible_events_by_date(self, user, date):
        try:
            membership = TeamMembership.objects.get(user=user, team=self)
            location_events = []
            phone_events = []
            if membership.role == TeamMembership.ROLE_ADMIN:
                attendance = self.attendance_set.filter(timestamp__date=date)
                checkins = self.checkin_set.filter(timestamp__date=date)
            elif membership.role == TeamMembership.ROLE_MEMBER:
                attendance = user.attendance_set.filter(timestamp__date=date)
                checkins = user.checkin_set.filter(timestamp__date=date)
                location_events = user.locationstatus_set.filter(timestamp__date=date)
                # phone_events = user.phonestatus_set.filter(timestamp__date=date)

            events = list(attendance) + list(checkins) + list(location_events) + list(phone_events)
            return self._sort_events(events)

        except ObjectDoesNotExist:
            pass

        return []

    def get_visible_events_by_page(self, user, start, limit):
        try:
            membership = TeamMembership.objects.get(user=user, team=self)
            location_events = []
            phone_events = []
            if membership.role == TeamMembership.ROLE_ADMIN:
                attendance = self.attendance_set.all().order_by('-timestamp')[0:start+limit]
                checkins = self.checkin_set.all().order_by('-timestamp')[0:start+limit]
            elif membership.role == TeamMembership.ROLE_MEMBER:
                attendance = user.attendance_set.all().order_by('-timestamp')[0:start+limit]
                checkins = user.checkin_set.all().order_by('-timestamp')[0:start+limit]
                location_events = user.locationstatus_set.all().order_by('-timestamp')[0:start+limit]
                # phone_events = user.phonestatus_set.all().order_by('-timestamp')[0:start+limit]

            events = list(attendance) + list(checkins) + list(location_events) + list(phone_events)
            events = self._sort_events(events)
            return events[start:start+limit]

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

class Checkin(BaseLocationModel):
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    description = models.TextField(blank=True)

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

class Attendance(BaseLocationModel):
    ACTION_SIGNIN = 'signin'
    ACTION_SIGNOUT = 'signout'

    ACTION_CHOICES = (
        (ACTION_SIGNIN, 'signin'),
        (ACTION_SIGNOUT, 'signout'),
    )

    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    message_id = models.CharField(max_length=40, unique=True)

def user_media_path(instance, filename):
    return 'teams/{0}/users/{1}/{2}/{3}'.format(
        instance.team.id, instance.user.id, instance.unique_id, filename)

class UserMedia(BaseModel):
    media = models.FileField(upload_to=user_media_path)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class Message(BaseModel):
    STATUS_SENT = 'sent'
    STATUS_DELIVERED = 'delivered'
    STATUS_READ = 'read'

    STATUS_CHOICES = (
        (STATUS_SENT, 'sent'),
        (STATUS_DELIVERED, 'delivered'),
        (STATUS_READ, 'read'),
    )

    id = models.CharField(max_length=16, primary_key=True, editable=False)
    thread = models.CharField(max_length=32)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_messages")
    target = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="recv_messages")
    body = models.TextField()
    original = models.TextField()

    def validate_next_status(self, status):
        if self.status == self.STATUS_SENT and status != self.STATUS_SENT:
            return status
        elif self.status == self.STATUS_DELIVERED and status == self.STATUS_READ:
            return status

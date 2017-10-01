from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models

from loco.models import BaseModel


class Team(BaseModel):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='creator')
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
                status = TeamMembership.STATUS_ACCEPTED
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
                status = TeamMembership.STATUS_INVITED
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


    STATUS_INVITED = 'invited'
    STATUS_ACCEPTED = 'accepted'

    STATUS_CHOICES = (
        (STATUS_INVITED, 'invited'),
        (STATUS_ACCEPTED, 'accepted'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="invites")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_INVITED)